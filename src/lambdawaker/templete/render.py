import json
import os.path
from io import BytesIO
from types import SimpleNamespace

from PIL import Image
from jinja2 import Template, Environment, FileSystemLoader, StrictUndefined

from lambdawaker.dataset.DiskDataset import DiskDataset
from lambdawaker.draw import card_background as card_background_module
from lambdawaker.draw.color.HSLuvColor import to_hsluv_color, HSLuvColor
from lambdawaker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawaker.file.path.ensure_directory import ensure_directory
from lambdawaker.file.path.wd import path_from_root
from lambdawaker.log.Profiler import Profiler
from lambdawaker.process.process_in_parrallel import process_parallel
from lambdawaker.reflection.query import select_random_function_from_module_and_submodules
from lambdawaker.templete.PlaywrightRenderer import PlaywrightRenderer
from lambdawaker.templete.fields import field_generators


def render_layer(page, html_content: str):
    """
    Renders HTML content to a PNG in memory, extracts bounding boxes, and specifically
    handles local image loading using Playwright's route() method.
    """

    captured_elements_data = []

    page.set_content(html_content)
    page.wait_for_selector('#view-port')

    card = page.query_selector('#view-port')
    image_bytes = card.screenshot(omit_background=True)

    elements = page.query_selector_all('*[capture="true"]')

    for i, element in enumerate(elements):
        bounding_box = element.bounding_box()

        if bounding_box:
            tag_name = element.evaluate('e => e.tagName')

            element_info = {
                "index": i,
                "tag": tag_name,
                "bounding_box": {
                    "x": bounding_box["x"],
                    "y": bounding_box["y"],
                    "width": bounding_box["width"],
                    "height": bounding_box["height"]
                },
                "source": element.get_attribute('src') if tag_name == 'IMG' else "Text Element"
            }
            captured_elements_data.append(element_info)

    return image_bytes, captured_elements_data


def render_layers(
        jinja_root,
        template_name,
        renderer,
        template_data=None,
        env=None,
        data=None
):
    profiler = Profiler(verbose=False)
    valid_extensions = ['.html', '.j2']
    layers_log = []
    layers = {}

    template_path = os.path.join(jinja_root, template_name)

    profiler.start("render_layers")

    jinja_env = Environment(
        loader=FileSystemLoader(str(jinja_root)),
        autoescape=False,
        undefined=StrictUndefined,  # fail loudly on missing vars
        trim_blocks=True,
        lstrip_blocks=True,
    )

    for template_file in os.listdir(template_path):
        file_ext = os.path.splitext(template_file)[1]

        if file_ext not in valid_extensions:
            continue

        layer_name = os.path.splitext(template_file)[0]
        profiler.start(f"rendering template: {layer_name}")

        file_ext = os.path.splitext(template_file)[1]
        if file_ext not in valid_extensions:
            continue

        component_path = os.path.join(template_name, template_file).replace('\\', '/')
        template = jinja_env.get_template(str(component_path))

        # render the templete text with Jinja2
        rendered_html_text = template.render(
            template_data=template_data,
            gen=field_generators,
            ds=renderer.data_source_handler,
            tx={
                "str": str,
                "len": len
            },
            env=env,
            data=data
        )

        # Then use headless Playwright to render the HTML to a PNG image
        image_bytes, captured_elements_data = render_layer(
            renderer.page, rendered_html_text
        )

        pil_image = Image.open(BytesIO(image_bytes))

        layers[layer_name] = SimpleNamespace(
            name=layer_name,
            elements=captured_elements_data,
            image=pil_image
        )

        layer_render_time = profiler.finalize(f"rendering template: {layer_name}")

        layers_log.append({
            "layer_name": layer_name,
            "layer_render_time": layer_render_time
        })

    render_time_layers_time = profiler.finalize("render_layers")

    log = {
        "render_time_layers_time": render_time_layers_time,
        "layers": layers_log
    }

    return log, layers


def render_template(jinja_root, template, renderer, env=None, data=None, cache=None):
    profiler = Profiler(verbose=False)

    cache = cache if cache is not None else {}

    profiler.start("render_template")
    profiler.start("load_template_data")

    template_path = os.path.join(jinja_root, template)
    common_data_path = os.path.join(template_path, "meta/common.json")

    if common_data_path not in cache:
        with open(common_data_path, 'r') as f:
            cache[common_data_path] = json.load(f)
    template_data = cache[common_data_path]

    meta_data_path = os.path.join(template_path, "meta/meta.json")
    if meta_data_path not in cache:
        with open(meta_data_path, 'r') as f:
            cache[meta_data_path] = json.load(f)

    meta_data = cache[meta_data_path]
    profiler.finalize("load_template_data")

    profiler.start("render_layers")

    layers_log, layers = render_layers(
        jinja_root,
        template,
        renderer=renderer,
        template_data=template_data,
        data=data,
        env=env
    )

    profiler.finalize("render_layers")

    profiler.start("add_background_layer")

    first_layer = layers[meta_data["order"][1]]

    profiler.start("select_background_paint_function")
    background_paint_function = select_random_function_from_module_and_submodules(card_background_module, "generate_card_background_.*")
    select_background_function_time = profiler.finalize("select_background_paint_function")

    paint_function_label = f"background_paint_function {background_paint_function.__name__}"
    profiler.start(paint_function_label)

    background_log, card_background = background_paint_function(
        first_layer.image.size,
        env["theme"]["primary_color"]
    )

    profiler.finalize(paint_function_label)

    layers["background_layer"] = SimpleNamespace(
        name="background_layer",
        elements=[],
        image=card_background
    )
    profiler.finalize("add_background_layer")

    render_template_time = profiler.finalize("render_template")

    log = {
        "render_template_time": render_template_time,
        "select_background_function_time": select_background_function_time,
        "layers_log": layers_log,
        "background_log": background_log,
    }

    return log, layers, meta_data


def render_record(renderer, record, record_id, cache=None):
    templates_root_path = path_from_root("assets/templates/")
    template = "A"

    primary_color = generate_hsluv_black_text_contrasting_color()
    text_color_hex = to_hsluv_color((0, 0, 0, 1))

    default_env = {
        "theme": {
            "primary_color": primary_color,
            "text_color": text_color_hex
        }
    }

    log, layers, meta_data = render_template(
        templates_root_path,
        template,
        env=default_env,
        data={
            "id": record_id,
            "record": record
        },
        renderer=renderer,
        cache=cache
    )

    bg_layer = layers["background_layer"]

    canvas = Image.new("RGBA", bg_layer.image.size)

    for name in meta_data["order"]:
        data = layers[name]
        canvas.paste(data.image, (0, 0), data.image)

    ensure_directory("./output/img/")
    canvas.save(f"./output/img/{record_id}.png")

    ensure_directory("./output/log/")

    with open(f"./output/log/{record_id}.json", 'w') as f:
        json.dump(
            log,
            f,
            default=lambda o: o.to_rgba_hex() if isinstance(o, HSLuvColor) else o.__dict__,
            indent=2
        )


process_env = {}


def proces_initializer():
    person_ds = DiskDataset("lambdaWalker/ds.photo_id")
    person_ds.load("@DS/lw_person_V0.0.0")
    renderer = PlaywrightRenderer([person_ds])
    cache = {}
    global process_env

    process_env = {
        "person_ds": person_ds,
        "renderer": renderer,
        "cache": cache
    }


def render_worker(record_id, skip_existing=True, env=None):
    env = env if env is not None else process_env

    person_ds = env["person_ds"]
    renderer = env["renderer"]
    cache = env["cache"]

    if not (skip_existing and os.path.exists(f"./output/{record_id}.png")):
        record = person_ds[record_id]
        render_record(
            record_id=record_id,
            record=record,
            renderer=renderer,
            cache=cache
        )


def render_single_record(record_id=0):
    person_ds = DiskDataset("lambdaWalker/ds.photo_id")
    person_ds.load("@DS/lw_person_V0.0.0")
    renderer = PlaywrightRenderer([person_ds])
    cache = {}

    render_record(renderer, person_ds[record_id], record_id, cache=cache)


def render_records_parallel(num_processes=None, skip_existing=True):
    temp_ds = DiskDataset("lambdaWalker/ds.photo_id")
    temp_ds.load("@DS/lw_person_V0.0.0")
    limit = len(temp_ds)
    del temp_ds
    # limit = 50

    process_parallel(
        list(range(limit)),
        render_worker,
        initializer=proces_initializer,
        kargs={"skip_existing": skip_existing},
        num_processes=num_processes
    )


if __name__ == "__main__":
    render_single_record()
    # render_records_parallel(skip_existing=False)

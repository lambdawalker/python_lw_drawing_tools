# **LW-PathResolver**

A Python utility for managing project path aliases. Replace hardcoded absolute paths with short, readable prefixes like @DS (Datasets) or @PRJ (Projects).

## **🚀 Key Features**

* **Standardized Aliases**: Use @NAME/path everywhere in your code.  
* **Auto-Directory Creation**: Automatically runs mkdir \-p on resolved paths by default.  
* **Smart Caching**: High performance. It only re-reads the config file if it has actually been saved/modified.  
* **Environment Fallback**: If an alias isn't in your config, it checks system Environment Variables automatically.  
* **Flexible Syntax**: Supports string calls resolve("@DS/file"), dictionary access resolve\["DS"\], or tuple pairs resolve\["DS", "file"\].

## **🛠 Setup**

1. Create the config file:  
   Create a file named .lw\_paths in your user home directory (\~/.lw\_paths or C:\\Users\\Name\\.lw\_paths).  
2. Define your paths:  
   Add entries using the KEY \= VALUE format. You can use \# for comments and even reference environment variables like $HOME.  
   \# \~/.lw\_paths  
   DS \= \~/data/datasets  
   PRJ \= /work/active\_projects  
   MODELS \= $HOME/local\_models

## **📖 Usage Examples**

### **1\. Basic Resolution**

from lw\_resolver import resolve

\# Resolves to "/home/user/data/datasets/raw/v1.csv"  
\# It also ensures the "raw" folder exists\!  
path \= resolve("@DS/raw/v1.csv")

with open(path, 'r') as f:  
    \# ...

### **2\. Dictionary-Style Access**

\# Get just the root directory for a project  
project\_root \= resolve\["PRJ"\]

\# Resolve using a tuple (useful for dynamic variables)  
category \= "processed"  
filename \= "output.parquet"  
full\_path \= resolve\[category, filename\]

### **3\. Iteration and Discovery**

\# List all active mappings  
for alias, path in resolve.items():  
    print(f"@{alias} \-\> {path}")

\# Check if an alias is defined  
if "MODELS" in resolve:  
    print("Model path is ready.")

### **4\. Advanced Options**

\# Disable auto-directory creation  
path \= resolve("@DS/temp.txt", make=False)

\# Force a fresh read of the .lw\_paths file  
path \= resolve("@PRJ/config.json", ignore\_cache=True)

\# Open your config file in the default editor  
\# resolve.edit\_config()

## **🔧 Technical Details**

The resolver uses pathlib internally, making it fully cross-platform (handling / vs \\ automatically).

* **Priority**: .lw\_paths file \> System Environment Variables.  
* **Caching**: Uses os.stat to check the file's st\_mtime (last modified time).
import os
import pathlib
a = [ pathlib.Path(f).name for f in os.listdir('C:\\Users\\HP\\Downloads\\')]
print(a)
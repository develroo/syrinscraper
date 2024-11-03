# syrinscraper 

This short python program reads the various `chapter.xml` files in a Syrinscape `Chapters` folder and symlinks them to a `done` directory with the names of the soundset and the name of element symlinked back to the `.syrin` file from the `a` folder. It then in turn symlinks this names soundset to a defined path, which by defult is `/home/$user/media/audio/soundsets` but it can be specified on the command line.


```
Usage: python syrinscrape.py chapter.xml [destination_folder]
Options:
  chapter.xml          Path to the XML file to parse
  [destination_folder] Optional destination folder for soundsets
```

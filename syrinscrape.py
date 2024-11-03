#!/usr/bin/python3
import os
import sys
import getpass
import xml.dom.minidom

def traverse_xml(element, sections):
    if element.nodeType == element.ELEMENT_NODE and element.tagName == "Samples":
        for sample_element in element.getElementsByTagName("SoundSample"):
            sample_data = {"Uuid": None, "Title": None, "SoundsetName": None}
            for child in sample_element.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    if child.tagName == "Uuid":
                        sample_data["Uuid"] = child.firstChild.data.strip()  # Strip whitespace
                    elif child.tagName == "Title":
                        sample_data["Title"] = child.firstChild.data.strip()  # Strip whitespace
            sections.append(sample_data)

    elif element.nodeType == element.ELEMENT_NODE and element.tagName == "Chapter":
        sample_data = {"SoundsetName": None}
        for child in element.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                if child.tagName == "Title":
                    sample_data["SoundsetName"] = child.firstChild.data.strip()  # Strip whitespace
        sections.append(sample_data)

    for child in element.childNodes:
        traverse_xml(child, sections)

def is_valid_symlink(path):
    return os.path.islink(path) and os.path.exists(os.path.realpath(path))

# Display help message if --help is passed
if '--help' in sys.argv:
    print("Usage: python syrinscrape.py chapter.xml [destination_folder]")
    print("Options:")
    print("  chapter.xml          Path to the XML file to parse")
    print("  [destination_folder] Optional destination folder for soundsets")
    sys.exit(0)

if len(sys.argv) < 2:
    print("Usage: python syrinscrape.py chapter.xml [destination_folder]")
    sys.exit(1)

xml_file = sys.argv[1]

# Get the destination folder from command line, or use the default
if len(sys.argv) >= 3:
    destination_folder = sys.argv[2]
else:
    username = getpass.getuser()  # Get the username of the user running the script
    destination_folder = f"/home/{username}/media/audio/soundsets/"

try:
    dom = xml.dom.minidom.parse(xml_file)
    root = dom.documentElement
    sections = []
    traverse_xml(root, sections)

    # Get the directory of the XML file
    xml_dir = os.path.dirname(os.path.abspath(xml_file))

    # Check if the 'done' folder exists in the XML directory, if not, create it
    done_folder = os.path.join(xml_dir, "done")
    if not os.path.exists(done_folder):
        os.makedirs(done_folder)
        print("Created 'done' folder.")

    soundset_name = None

    for section in sections:
        if section.get("SoundsetName"):
            soundset_name = section["SoundsetName"]
            break

    if soundset_name:
        # Replace spaces with underscores in the soundset name
        soundset_name = soundset_name.replace(" ", "_")
        soundset_folder = os.path.join(done_folder, soundset_name)
        
        # Create soundset folder inside the 'done' folder
        if not os.path.exists(soundset_folder):
            os.makedirs(soundset_folder)
            print(f"Created soundset folder: {soundset_folder}")

    for section in sections:
        if section.get("Uuid") and section.get("Title"):
            # Create symlinks with valid paths inside soundset folder
            uuid_filename = section["Uuid"] + ".syrin"
            title_filename = section["Title"] + ".ogg"
            src = os.path.abspath(os.path.join("a", uuid_filename))  # Get absolute path for symlink source
            dst = os.path.abspath(os.path.join(soundset_folder, title_filename))  # Get absolute path for symlink destination
            try:
                os.symlink(src, dst)
                print(f"Created symlink: {dst} -> {src}")
            except FileExistsError:
                print(f"Symlink already exists: {dst} -> {src}")

except FileNotFoundError:
    print("XML file not found.")

except Exception as e:
    print("An error occurred:", e)

finally:
    dom.unlink()  # Ensure XML object is cleaned up

# Create symlink from soundset folder to the destination folder
if soundset_name:
    soundset_path = os.path.abspath(os.path.join(destination_folder, soundset_name))
    try:
        os.symlink(soundset_folder, soundset_path)
        print(f"Created soundset symlink: {soundset_path} -> {soundset_folder}")
    except FileExistsError:
        print(f"Soundset symlink already exists: {soundset_path} -> {soundset_folder}")

    # Verify symlink
    if os.path.islink(soundset_path):
        print(f"Soundset symlink '{soundset_path}' is valid.")
    else:
        print(f"Soundset symlink '{soundset_path}' is invalid.")

# Verify symlinks
print("\nVerifying symlinks...")
for section in sections:
    if section.get("Uuid") and section.get("Title"):
        title_filename = section["Title"] + ".ogg"
        dst = os.path.abspath(os.path.join(soundset_folder, title_filename))
        if is_valid_symlink(dst):
            print(f"Symlink '{dst}' is valid.")
        else:
            print(f"Symlink '{dst}' is invalid.")

import os

def list_dir(fld):
    for fn in os.listdir(fld):
        print(fn)


list_dir("D:\\Sources\\Learning\\Python\\Practices and Projects\\web_scrapping")
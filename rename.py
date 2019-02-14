import os
def main():
    for file_name in os.listdir(os.getcwd()):
        if file_name == __file__:
            continue
        target_dir = f"./{file_name}/.config/{file_name}"
        parent_dir = f"{os.getcwd()}/{file_name}"
        print(f"creating directory {target_dir}")
        try:
            os.makedirs(target_dir)
        except Exception as e:
            pass
        #for sub_file in os.listdir(parent_dir):
            #if sub_file != '.config':
                #print(f"moving {parent_dir}/{sub_file} into {target_dir}/{sub_file}")
                #os.rename(f"{parent_dir}/{sub_file}", "{target_dir}/{sub_file}")


if __name__ == '__main__':
    main()

# import face_recognition
# from common_functions import *
# import os
# import re

# SAVE_DATA_PATH = PROJECT_PATH + 'Data/"

# def image_files_in_folder(folder):
#     return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

# if __name__ == "__main__":
#     list_folder = ['test', 'train']
#     for folder in list_folder:
#         for class_dir in os.listdir(DATA_PATH):
#             if not os.path.isdir(os.path.join(DATA_PATH, class_dir)):
#                 continue

#             # Loop through each training image for the current person and past image path for encoing individualy
#             for img in image_files_in_folder(os.path.join(DATA_PATH, class_dir, folder)):
#                 path = img.split('/')
#                 user_ID = path[-3]
#                 img_name = path[-1]

#                 SAVE_PATH = SAVE_DATA_PATH + folder
#                 os.chdir(SAVE_PATH + '/' + user_ID) 
#                 loaded_img = cv2.imread( img )
                
#                 # Identifying face_locations in the images
#                 max_fra = max( loaded_img.shape[0], loaded_img.shape[1] ) / glo_va.IMAGE_SIZE
#                 new_height = int( loaded_img.shape[0] / max_fra )
#                 new_width = int( loaded_img.shape[1] / max_fra )

#                 resized_img = cv2.resize(loaded_img, ( new_width, new_height ))
#                 RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

#                 face_locations = face_recognition.face_locations(RGB_resized_img)
#                 count = 0
#                 for (top, right, bottom, left) in face_locations:
#                     top *= max_fra
#                     bottom *= max_fra
#                     left *= max_fra
#                     right *= max_fra

#                     img_name_1 = str(count)+'-'+img_name
#                     cv2.imwrite(img_name_1, loaded_img[int(top):int(bottom),int(left):int(right)]) 
#                     count += 1
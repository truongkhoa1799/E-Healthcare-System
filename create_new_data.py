###############################################################################################
# __LoadNewData                                                                               #                    
# Input:                                                                                      #
#   None            None                        :   None                                      #
# Output:                                                                                     #
#   ret                                         :   -1 No Data Loaded, 0 success              #
###############################################################################################
def __LoadNewData():
    time_request = time.time()

    # Creating a list that store each encoding thread
    list_thread_encoding_image = []

    # Loop through each person in the training set
    for class_dir in os.listdir(FACE_TRAIN_PATH):
        print(class_dir)
        if not os.path.isdir(os.path.join(FACE_TRAIN_PATH, class_dir)):
            continue
    
        # Loop through each training image for the current person and past image path for encoing individualy
        for img in __image_files_in_folder(os.path.join(FACE_TRAIN_PATH, class_dir)):
            path = img.split('/')
            user_ID = class_dir
            img_name = path[-1]
            loaded_img = cv2.imread( img )
            print("Loaded image {} ".format(img_name))
            
            # embedded_face: type ndarray (256,)
            # embedded_face = __face_iden(loaded_img)
            fra = IMAGE_SIZE / max(loaded_img.shape[0], loaded_img.shape[1]) 
            resized_img = cv2.resize(loaded_img, (int(loaded_img.shape[1] * fra), int(loaded_img.shape[0] * fra)))
            RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
            embedded_face = face_encodings(RGB_resized_img, [(0,150,150,0)])[0]
            # embedded_face = np.array(embedded_face).reshape(-1,1)
            # print(type(embedded_face))
            # print(embedded_face.shape)
            # embedded_face = embedded_face.reshape((1,len(embedded_face)))
            # print(type(embedded_face))
            # print(embedded_face.shape)

            __known_face_encodings.append(embedded_face)
            __known_face_IDs.append(user_ID)

    print("\ttime load data {}".format(time.time() - time_request))
    print("\t{}".format(__known_face_IDs))

    if len(__known_face_encodings) != len(__known_face_IDs) \
        or len(__known_face_encodings) == 0 \
        or len(__known_face_IDs) == 0:
        return -1

    __SaveData()
    return 0

###############################################################################################
# __SaveData                                                                                  #                    
# Input:                                                                                      #
#   None            None                        :   None                                      #
# Output:                                                                                     #
#   ret             int                         :   -1 No Data Loaded, 0 success              #
###############################################################################################
def __SaveData():
    with open(PATH_USER_ID, mode='wb') as fp_1:
        pickle.dump(__known_face_IDs, fp_1)
    
    with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
        pickle.dump(__known_face_encodings, fp_2)
    
def __image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

#################################################################################
# __SaveKNNModel                                                                #                    
# Input:                                                                        #
#   knn_clf         :   Model after trained                                     #
#   model_save_path :   path to save model                                      #
# Output:                                                                       #
#   ret             :   -1 no path, 0 success                                   #
#################################################################################
def __SaveKNNModel( knn_clf,model_save_path):
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

###############################################################################################
# __TrainKNN                                                                                  #                    
# Input:                                                                                      #
#   int             n_neighbors                 :   Bumber of neighbors                       #
#   str             knn_algorithm               :   algorithm implement KNN                   #
#   str             knn_weights                 :   weights to calculate diff                 #
# Output:                                                                                     #
#   knn_clf         knn_clf                     :   knn classification model                  #
###############################################################################################
def __TrainKNN( n_neighbors, knn_algorithm, knn_weights, model_save_path):
    print("Starting train KNN Model")
    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(__known_face_encodings))))
        print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algorithm, weights=knn_weights)

    # __known_face_encodings is list of ndarray
    # __known_face_IDs is list of str
    knn_clf.fit(__known_face_encodings, __known_face_IDs)

    ret = __SaveKNNModel(knn_clf, KNN_MODEL_PATH)

    print("Finishing train KNN Model")
    return knn_clf
`merge_translates.py` is aimed for generate `output/translates.csv` with *android+ios=general* translates and unique platform translates, the translates separated by empty row, first section includes general translates, second only android translates, third section only iOS translates.

    ios_project_path = "path_to_project/allright-ios-app"
    android_project_path = "path_to_project/allright-android-app"

`ios_project_path` and `android_project_path` is required path to iOS and Android project for merge platfor translates.

`generate_translates.py` is aimed for generate platform string resources from `res/csv/translates.csv`, output files will `output/generate`
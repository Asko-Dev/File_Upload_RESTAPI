#An API endpoint for file upload:
- User Registration
- User Token Authentication
- User Details display (based on the token loaded)
- API root for Tag API, File Upload API, Public Files API
- Tag API -> create tags to assign to your files when POSTing files
- Upload File API ->
    - Upload and name files [validator for extensions]
    - Choose Private/Public privacy settings [Private visible only to owner]
    - Add Tags to your files
    - Add description
    - Date automatically set
- SHA-512 hash of the file created on save() of the model
    - visible only on the admin site
- Public File API ->
    - Public files of all users displayed
- Filtering based on tags and privacy settings for both Private and Public API

#DEPLOYED TO HEROKU (Using AWS S3 Bucket for storage)
ROOT URL: https://asko-fileupload.herokuapp.com

URL endpoints:
/api/user-create/                                       POST
/api/user-token/                                        GET
/api/user-me/                                           GET/PUT/PATCH
/api/tag/                                               GET/POST
/api/tag/<pk>                                           GET/PUT/PATCH/DELETE
/api/file-upload/                                       GET/POST
/api/file-upload/<pk>                                   GET/PUT/PATCH/DELETE
/api/file-upload/?tag=<pk>&visibility='PRV'/'PUB'       GET/PUT/PATCH/DELETE
/api/public-uploads/                                    GET
/api/public-uploads/<pk>                                GET
/api/public-uploads/?tag=<pk>&visibility='PRV'/'PUB'    GET

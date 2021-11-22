from utils.methods import extract_face
from PIL import Image
from io import BytesIO
import base64
import db.setup as s

# with Image.open("test/t1.jpg") as im:
#     im.rotate(45).show()

#     output = BytesIO()
#     im.save(output, format="png")
#     image_as_string = output.getvalue()
#     extract_face(image_as_string)

#with open("test/t1.jpg", "rb") as image_file:
#    encoded_string = base64.b64encode(image_file.read())

#im_bytes = base64.b64decode(encoded_string)
#extract_face(im_bytes)

con = s.create_connection()
#s.create_tables(con)
s.test_arr(con)
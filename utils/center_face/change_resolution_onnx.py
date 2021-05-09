import onnx
import math

# input_size =(320,254)
input_size =(224,128)
model = onnx.load_model("/home/thesis/Documents/thesis/E-Healthcare-System/utils/center_face/centerface.onnx")
d = model.graph.input[0].type.tensor_type.shape.dim
# print("In", d)
# for output in model.graph.output:
#     d = output.type.tensor_type.shape.dim
#     print("Out:", d)
rate = (int(math.ceil(input_size[0]/d[2].dim_value)),int(math.ceil(input_size[1]/d[3].dim_value)))
print("rate",rate)
d[0].dim_value = 1
d[2].dim_value *= rate[1]
d[3].dim_value *= rate[0]
for output in model.graph.output:
    d = output.type.tensor_type.shape.dim
    print(d)
    d[0].dim_value = 1
    d[2].dim_value  *= rate[1]
    d[3].dim_value  *= rate[0]

onnx.save_model(model,"centerface_224_128.onnx" )
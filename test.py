import pycuda.driver as cuda

print(cuda.Device(0).count())
# cuda.Context.pop()
# cuda_ctx = cuda.Device(0).make_context()
# cuda_ctx.pop()
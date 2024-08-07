import os
import torch
import torch.nn as nn
from torchvision.models import resnet18
from fastapi import FastAPI, Request, Response
import io

class ResNetServer(nn.Module):
    def __init__(self, num_classes=10):
        super(ResNetServer, self).__init__()
        resnet = resnet18()
        self.remaining_layers = nn.Sequential(*list(resnet.children())[6:-1])  # layer3, layer4, avgpool
        
        # Final classifier: This replaces the fc layer in ResNet
        self.fc = nn.Linear(resnet.fc.in_features, num_classes)

    def forward(self, x):
        x = self.remaining_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x

app = FastAPI()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = ResNetServer()
model.load_state_dict(torch.load('resnet.pth', map_location=device), strict=False)
model.to(device)
model.eval()


@app.post("/process")
async def process_tensor(request: Request):
    try:
        tensor_data = await request.body()
        
        buffer = io.BytesIO(tensor_data)
        tensor = torch.load(buffer, map_location=device)

        with torch.inference_mode():
            result = model(tensor)
            softmax_outputs = nn.functional.softmax(result, dim=1)
            _, predicted = torch.max(softmax_outputs, dim=1)
        
        output_buffer = io.BytesIO()
        torch.save(predicted, output_buffer)
        output_buffer.seek(0)
        
        return Response(content=output_buffer.getvalue(), media_type="application/octet-stream")
    except Exception as e:
        return Response(content=f"An error occurred: {str(e)}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

import timm
import torch
import torch.nn as nn

class BaseModel(nn.Module):
    def __init__(self, model_name, pretrained, num_classes, in_chans):
        super(BaseModel, self).__init__()
        self.base_model = timm.create_model(model_name=model_name, pretrained=pretrained, num_classes=num_classes, in_chans=in_chans)

    def forward(self, x):
        x = self.base_model(x)
        return x
    
    

class MLP_layer(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        self.num_features = self.base_model.num_features

        # 마블링, 조직감, 기호도를 위한 MLP
        self.marbling_texture_total = nn.Sequential(
            nn.Linear(self.num_features, 256),
            nn.ReLU(),
            nn.Linear(256, 3)
        )
        
        # 표면육즙을 위한 MLP
        self.moisture_head = nn.Sequential(
            nn.Linear(self.num_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        # 색깔을 위한 MLP
        self.color_head = nn.Sequential(
            nn.Linear(self.num_features, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, x):
        base_output = self.base_model(x)
        
        features = base_output

        marbling_texture_total = self.marbling_texture_total(features)
        moisture = self.moisture_head(features)
        color = self.color_head(features)
        
        # 원래의 라벨 순서대로 출력을 결합
        return torch.cat([
            marbling_texture_total[:, 0:1],  # 마블링
            color,  # 색깔
            marbling_texture_total[:, 1:2],  # 조직감
            moisture,  # 표면육즙
            marbling_texture_total[:, 2:3]  # 기호도
        ], dim=1)
    

def create_model(model_name, pretrained, num_classes, in_chans, out_dim):

    if out_dim != 5:
        raise ValueError("out_dim must be exactly 5 for this model")

    base_model = BaseModel(model_name, pretrained, num_classes, in_chans)
    model = MLP_layer(base_model)

    return model

from fastapi import APIRouter
import os
from pyvis import network as net

kmap_router = APIRouter(tags=["k-map"])

@kmap_router.get("/kmap")
def gen_k_map():
    kmap=net.Network(height="750px",width="750px",bgcolor="#FFFFFF",font_color="black",directed=True)

    nodes={
        "工業自動化":["感測器技術","控制系統","通訊協議","自動化設備","工業IoT","安全與維護"],
        "感測器技術":["溫度感測器","壓力感測器","光電感測器"],
        "控制系統":["PLC","SCADA","HMI"],
        "通訊協議":["Modbus","OPC UA","Ethernet/IP"],
        "自動化設備":["工業機械手臂","自動化輸送帶","AGV"],
        "工業IoT":["邊緣運算","雲端資料平台","數據視覺化"],
        "安全與維護":["異常偵測","預測性維護","工業資安"]
        }

    for parent,children in nodes.items():
        kmap.add_node(parent,label=parent)
        for child in  children:
            kmap.add_node(child,label=child)
            kmap.add_edge(parent,child)
    
    kmap.set_options("""
        var options={
        "nodes":{"font":{"size":16},"shape":"box"},
        "edges":{"arrows":{"to":{"enabled":true}}},
        "physics":{"enabled":true}
        }
    """)

    os.makedirs("static", exist_ok=True)
    out_file = os.path.join("static", "map.html")
    kmap.write_html(out_file)

    return {"map_url":"/static/map.html"}
from flask import Blueprint, jsonify
from Enterprise.model.glo import Glo
from Enterprise.service.get_data import GetData
from Enterprise.service.interpersonal_network import InterpersonalNetwork

# 人际关系网络
GetData.load_data()
interpersonal_network = InterpersonalNetwork()
for i in range(0, len(Glo.from_email)):
    interpersonal_network.add_node(Glo.from_email[i], Glo.to_email[i])
node = []  # node的值要乘以5，以免太小了显示不出来
link = []
outDegree = interpersonal_network.outDegree  # 由于不显示有向图，进这个属性就足够了
print(outDegree)
for from_email in outDegree.keys():
    to_emails = outDegree[from_email]
    tmp_count = 0
    for to_email in to_emails.keys():
        tmp_count += to_emails[to_email] * 5
        link.append({
            "source": from_email,
            "target": to_email,
            "weight": to_emails[to_email]
        })
    node.append({
        "name": from_email,
        "symbolSize": tmp_count
    })
ret_data = {"node": node, "link": link}
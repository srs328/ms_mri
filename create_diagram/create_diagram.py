import numpy as np
from PIL import Image
import pandas as pd
import sys

color_assignment_file = sys.argv[1]
if len(sys.argv) < 3:
    save_name = "thalamus_diagram.png"
else:
    save_name = sys.argv[2]

def get_color(ref, bin):
    return np.array((ref.loc[bin, "R"], ref.loc[bin, "G"], ref.loc[bin, "B"], 255))

template_image = Image.open("template_diagram.png")
template = np.asarray(template_image)
# color_ref = pd.read_csv("color_reference.csv", index_col="bin")
color_ref = pd.read_csv("color_reference_hot_CP.csv", index_col="bin")

diagram_ref_table = pd.read_csv("structure_reference.csv")
diagram_ref = diagram_ref_table['diagram_index']
diagram_ref.index = pd.MultiIndex.from_frame(diagram_ref_table[['Side', 'struct_index']])

color_value_table = pd.read_csv(color_assignment_file)
color_values = color_value_table['bin']
color_values.index = pd.MultiIndex.from_frame(color_value_table[['Side', 'struct_index']])

diagram = template.copy()
for struct, index in diagram_ref.items():
    bin = color_values[struct]
    color = get_color(color_ref, bin)
    template_inds = np.where(template[:, :, 0] == index)
    diagram[template_inds[0], template_inds[1], :] = color

background_inds = np.where(diagram[:, :, 3] == 0)
diagram[background_inds[0], background_inds[1], :] = np.array([255, 255, 255, 255])

diagram_image = Image.fromarray(diagram)
diagram_image.save(save_name)
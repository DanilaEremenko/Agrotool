from shapely.geometry import Polygon, Point

# TODO fill all textures
texture_conc_dict = {

    "sandy clay": {
        "conc_avg": {'sand': 45, 'clay': 30, 'silt': 5},
        "polygon": Polygon(((45, 55), (45, 35), (65, 35))),
        "textType": 10
    },
    "loam": {
        "conc_avg": {'sand': 40, 'clay': 20, 'silt': 40},
        "polygon": Polygon(((43, 7), (53, 7), (53, 20), (45, 27), (23, 27))),
        "textType": 4
    }

}


def get_info_by_texture(texture):
    if texture in texture_conc_dict.keys():
        return texture_conc_dict[texture]
    else:
        raise Exception("Unexpected texture name = %s" % str(texture))


def get_texture_by_conc(sand, clay, silt):
    if ((sand is None) or (silt is None) or (clay is None)):
        return None, -1
    for texture in texture_conc_dict.keys():
        if texture_conc_dict[texture]['polygon'].contains(Point(sand, clay)):
            return texture, texture_conc_dict[texture]['textType']

    raise Exception("No texture with (sand, clay, silt) = (%d %d %d)" % (sand, clay, silt))


if __name__ == '__main__':
    texture, textType = get_texture_by_conc(55, 40, 5)
    print("texture by conc  : name = %s, textType = %d" % (texture, textType))

    conc = get_info_by_texture('sandy clay')
    print("conc by texture  : conc =  %s" % str(conc))

from shapely.geometry import Polygon, Point

# TODO fill conc_avg
texture_conc_dict = {
    "sand": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((100, 0), (90, 10), (85, 0))),
        "textType": 1
    },
    "loamy sand": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((85, 0), (90, 10), (85, 15), (70, 0))),
        "textType": 2
    },
    "sandy loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((70, 0), (85, 15), (80, 20), (52, 20), (52, 7), (42.5, 7.5), (50, 0))),
        "textType": 3
    },
    "loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((52, 7), (52, 20), (45, 27.5), (22.5, 27.5), (42.5, 7.5))),
        "textType": 4
    },
    "silt": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((20, 0), (7, 13), (0, 13), (0, 0))),
        "textType": 5
    },
    "silt loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((50, 0), (22.5, 27.5), (0, 27.5), (0, 13), (7, 13), (20, 0))),
        "textType": 6
    },
    "sandy clay loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((80, 20), (65, 35), (45, 35), (45, 27.5), (52, 20))),
        "textType": 7
    },
    "clay loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((45, 27.5), (45, 40), (20, 40), (20, 27.5),)),
        "textType": 8
    },
    "silty clay loam": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((20, 27.5), (20, 40), (0, 40), (0, 27.5))),
        "textType": 9
    },
    "sandy clay": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((65, 35), (45, 55), (45, 35))),
        "textType": 10
    },
    "silty clay": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((20, 40), (0, 60), (0, 40))),
        "textType": 11
    },
    "clay": {
        "conc_avg": {'sand': None, 'clay': None, 'silt': None},
        "polygon": Polygon(((45, 40), (45, 55), (0, 100), (0, 60), (20, 40))),
        "textType": 12
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

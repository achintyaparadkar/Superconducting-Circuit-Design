# %%
# ===================================================================================
# IMPORT LIBRARIES AND LAYOUTS
# ===================================================================================
from numpy import pi
import gdspy
import gdslib
from SPCV4_Definitions import *

# ===================================================================================
# STANDARD EBL CROSS-DOT TYPE ALIGNMENT MARKER DEFINITION
# ===================================================================================

def EBLmarker(xpos, ypos, markersize, markergap, extension, layer, dt):
    alignmarker = gdspy.Rectangle(
        (xpos, ypos), (xpos - markersize, ypos - markersize))                        # cross dot
    hmarker1 = gdspy.Rectangle(
        (xpos - markergap - markersize, ypos),
        (xpos - markergap - markersize - extension, ypos - markersize))              # cross horizontal
    vmarker1 = gdspy.Rectangle(
        (xpos, ypos - markergap - markersize),
        (xpos - markersize, ypos - markergap - markersize - extension))              # cross vertical

    hmarker2 = gdspy.Rectangle(
        (xpos + markergap, ypos),
        (xpos + markergap + extension, ypos - markersize))                           # cross horizontal
    vmarker2 = gdspy.Rectangle(
        (xpos, ypos + markergap),
        (xpos - markersize, ypos + markergap + extension))                           # cross vertical

    marker = gdspy.fast_boolean(
        (alignmarker, hmarker1, vmarker1, hmarker2), vmarker2,
        operation='or', datatype=dt, layer=layer)

    return marker

# ===================================================================================
# STANDARD FLIP-CHIP BOX-TYPE ALIGNMENT MARKER DEFINITION
# ===================================================================================

def FCmarker(xpos, ypos, markersize, markergap, extension, layer, dt):

    # Squares for flip-chip alignment
    a = gdspy.Rectangle(
        (xpos, ypos),
        (xpos - extension - markersize, ypos - extension - markersize))              # bottom left square

    b = gdspy.Rectangle(
        (xpos + markersize, ypos),
        (xpos + 2*markersize + extension, ypos - extension - markersize))            # bottom right square

    c = gdspy.Rectangle(
        (xpos, ypos + markersize),
        (xpos - extension - markersize, ypos + 2*markersize + extension))            # top left square

    d = gdspy.Rectangle(
        (xpos + markersize, ypos + markersize),
        (xpos + 2*markersize + extension, ypos + 2*markersize + extension))          # top right square

    marker = gdspy.fast_boolean(
        (a, b, c), d, operation='or', datatype=dt, layer=layer)

    return marker

# %%
# ===================================================================================
# FEEDLINE
# ===================================================================================

def feedline1(Feed_x, Feed_y, layer, dt, device, noholesarea):                       # feedline with straight pad and bent feed
    cpwfeed = gdslib.CPWPath(CWpad, CGpad, layer, datatype=dt, cellName=device)
    cpwfeed.start([Feed_x, Feed_y], '+x')
    cpwfeed.openGap(Feed_pad/2)
    cpwfeed.straight(Feed_pad)
    cpwfeed.straight(Feed_pad, widthEnd=CWt, gapEnd=CGt)
    cpwfeed.straight(Feed_offset1)
    cpwfeed.bend(Feed_bend, 'r')

    cpwfeed.straight(Feed_offset2)
    cpwfeed.bend(Feed_bend, 'l')
    cpwfeed.straight(Feed_len)
    cpwfeed.bend(Feed_bend, 'l')
    cpwfeed.straight(Feed_offset2)
    cpwfeed.bend(Feed_bend, 'r')
    cpwfeed.straight(Feed_offset1)

    cpwfeed.straight(Feed_pad, widthEnd=CWpad, gapEnd=CGpad)
    cpwfeed.straight(Feed_pad)
    cpwfeed.openGap(Feed_pad/2)
    cpwfeed.end()

    feed = cpwfeed.makePolySet(cpwfeed.path)
    feed = gdspy.boolean(feed, None, "or", layer=layer, datatype=dt)

    geo_offset = gdspy.offset(feed, cheesing_offset,
                              join_first=False, layer=13)

    noholes = gdspy.boolean(
        (noholesarea, geo_offset),
        gdspy.Rectangle(
            (Feed_x+150, Feed_y-140),
            (Feed_x+660, Feed_y+140)), "or", layer=13)

    noholes = gdspy.boolean((
        noholes, geo_offset),
        gdspy.Rectangle(
            (Feed_x+660, Feed_y-30),
            (Feed_x+750, Feed_y+30)), "or", layer=13)

    noholes = gdspy.boolean(noholes, gdspy.Rectangle(
        (Feed_x+Feed_len+4*Feed_pad+Feed_offset2+2*Feed_bend+40, Feed_y-140),
        (Feed_x+Feed_len+4*Feed_pad+Feed_offset2+2*Feed_bend+540, Feed_y+140)),
        "or", layer=13)

    noholes = gdspy.boolean(noholes, gdspy.Rectangle(
        (Feed_x+Feed_len+4*Feed_pad+Feed_offset2+2*Feed_bend+100, Feed_y-30),
        (Feed_x+Feed_len+4*Feed_pad+Feed_offset2+2*Feed_bend-100, Feed_y+30)),
        "or", layer=13)

    yres = Feed_y - Feed_offset2 - 2*Feed_bend

    return feed, noholes, yres

def feedline2(Feed_x, Feed_y, layer, dt, device, noholesarea):                       # feedline with straight pad and straight feed
    cpwfeed = gdslib.CPWPath(CWpad, CGpad, layer, datatype=dt, cellName=device)
    cpwfeed.start([Feed_x, Feed_y], '+x')
    cpwfeed.openGap(Feed_pad/2)
    cpwfeed.straight(Feed_pad)
    cpwfeed.straight(Feed_pad, widthEnd=CWt, gapEnd=CGt)

    cpwfeed.straight(Feed_len)

    cpwfeed.straight(Feed_pad, widthEnd=CWpad, gapEnd=CGpad)
    cpwfeed.straight(Feed_pad)
    cpwfeed.openGap(Feed_pad/2)
    cpwfeed.end()

    feed = cpwfeed.makePolySet(cpwfeed.path)
    feed = gdspy.boolean(feed, None, "or", layer=layer, datatype=dt)

    geo_offset = gdspy.offset(feed, cheesing_offset,
                              join_first=False, layer=13)

    block1 = gdspy.Polygon(
        ((Feed_x+Feed_pad/2, Feed_y+Feed_pad/2),
        (Feed_x+3*Feed_pad/2, Feed_y+Feed_pad/2),
        (Feed_x+5*Feed_pad/2, Feed_y+CWt/2),
        (Feed_x+5*Feed_pad/2, Feed_y-CWt/2),
        (Feed_x+3*Feed_pad/2, Feed_y-Feed_pad/2),
        (Feed_x+Feed_pad/2, Feed_y-Feed_pad/2)))

    block2 = gdspy.Polygon(
        ((Feed_x+Feed_len+4*Feed_pad+Feed_pad/2, Feed_y+Feed_pad/2),
        (Feed_x+Feed_len+4*Feed_pad-Feed_pad/2, Feed_y+Feed_pad/2),
        (Feed_x+Feed_len+4*Feed_pad-3*Feed_pad/2, Feed_y+CWt/2),
        (Feed_x+Feed_len+4*Feed_pad-3*Feed_pad/2, Feed_y-CWt/2),
        (Feed_x+Feed_len+4*Feed_pad-Feed_pad/2, Feed_y-Feed_pad/2),
        (Feed_x+Feed_len+4*Feed_pad+Feed_pad/2, Feed_y-Feed_pad/2)))

    device.add(block1)
    device.add(block2)

    noholes = gdspy.boolean(
        (noholesarea, geo_offset),
        (block1, block2), "or", layer=13)

    yres = Feed_y

    return feed, noholes, yres


# %%
# ===================================================================================
# CPW MEANDERING RESONATOR DEFINITION
# ===================================================================================

def CPW_Res(i, xr, yr, reslength, layer, dt, device, noholesarea):

    meanderLen = reslength - C_len0 - neck - pi * bendRad
    turns = meanderLen // (MW[i] + pi*MG[i]/2)
    diff = meanderLen % (MW[i] + pi*MG[i]/2)
    neckangle = 'l' if direction[i] == '+x' else 'r'
    meanderangle = 'rr' if direction[i] == '+x' else 'll'
    open_gap = CW[i]+2*CG[i]

    cpw = gdslib.CPWPath(CW[i], CG[i], layer, datatype=dt, cellName=device)
    cpw.start([xr, yr], direction[i])
    cpw.openGap(open_gap)

    cpw.straight(C_len0)
    cpw.bend(bendRad, neckangle)

    cpw.straight(neck)
    cpw.bend(bendRad, neckangle)

    cpw.meander((MW[i] + pi*MG[i]/2)*turns, MG[i] / 2, MW[i], meanderangle)
    cpw.straight(diff)
    cpw.end()

    res = cpw.makePolySet(cpw.path)

    geo_offset = gdspy.offset(res, cheesing_offset,
                              join_first=False, layer=13)

    geo_offset = gdspy.boolean(geo_offset, None, "or", layer=layer, datatype=dt)
    noholes = gdspy.boolean(noholesarea, geo_offset,
                            "or", layer=13)

    return res, noholes

# %%
# ===================================================================================
# FLUX TUNABLE RESONATOR DEFINITION
# ===================================================================================

def CPW_SQUID(i, xr, yr, reslength, loop, junction, layer, dt, device, noholesarea):

    meanderLen = reslength - C_len - neck - 3*pi/2 * bendRad - (MW[i]/2-bendRad)
    turns = meanderLen // (MW[i] + pi*MG[i]/2)
    diff = meanderLen % (MW[i] + pi*MG[i]/2)

    startneckangle = 'l' if direction[i] == '+x' else 'r'
    startstraightangle = 'l' if direction[i] == '+x' else 'r'
    meanderangle = 'rr' if direction[i] == '+x' else 'll'
    open_gap = CW[i]+2*CG[i]

    cpw = gdslib.CPWPath(CW[i], CG[i], layer, datatype=dt, cellName=device)
    cpw.start([xr, yr], direction[i])
    cpw.openGap(open_gap)

    cpw.straight(C_len)
    cpw.bend(bendRad, startneckangle)

    cpw.straight(neck)
    cpw.bend(bendRad, startstraightangle)

    cpw.meander((MW[i] + pi*MG[i]/2)*turns, MG[i] / 2, MW[i], meanderangle)

    cpw.straight(MW[i]/2-bendRad)

    if direction[i] == '+x':
        if turns % 2 == 1:
            cpw.bend(bendRad, 'l')
        else:
            cpw.bend(bendRad, 'r')

    else:
        if turns % 2 == 1:
            cpw.bend(bendRad, 'r')
        else:
            cpw.bend(bendRad, 'l')

    cpw.straight(diff)
    cpw.openGap(1.5*open_gap)

    res = cpw.makePolySet(cpw.path)

    if direction[i] == '+x':
        xs = xr + open_gap + C_len - MW[i]/2
    else:
        xs = xr + open_gap - C_len + MW[i]/2 - 28

    ys = yr + neck + 3*bendRad + MG[i]*turns + diff + loop + 2*padwidth

    squidloop = SQUID_Loop(i, xs, ys, loop, junction, 0, 2, device)
    SQUID_Junctions(i, xs, ys, loop, junction, 0, 2, device)

    res = gdspy.boolean(res, squidloop[0], "or")
    res = gdspy.boolean(res, squidloop[1], "not", layer=layer, datatype=dt)

    geo_offset = gdspy.offset(res, cheesing_offset, join_first=False, layer=13)
    noholes = gdspy.boolean(noholesarea, geo_offset, "or", layer=13)

    return res, noholes, xs, ys

# %%
# ===================================================================================
# SQUID LOOP DEFINITION
# ===================================================================================

def SQUID_Loop(i, xs, ys, loop, junction, angle, num, device):

    looppatch = gdspy.Rectangle(
        (xs - loop/2 - 1.5*padwidth, ys - loop - 2*padwidth),
        (xs + loop/2 + 1.5*padwidth,
         ys + padwidth))
    looppatch = looppatch.fillet(outer_fillet/2)

    side = loop + padwidth
    contactpadwidth = CW[i]

    jspace1 = gdspy.Rectangle((xs - loop/2 - padwidth,
                               ys + 2*ext),
                              (xs - ext - loop/2 + inner_fillet/2 + 1,
                               ys + ext - padwidth - 1))

    jspace2 = gdspy.Rectangle((xs + loop/2 + padwidth,
                               ys + 2*ext),
                              (xs + ext + loop/2 - inner_fillet/2 - 1,
                               ys + ext - padwidth - 1))

    electrode_gap1 = gdspy.Rectangle((xs + ext/2 + loop/2 - inner_fillet/2,
                               ys - 1),
                              (xs + loop/2 - inner_fillet/2,
                               ys + 1))

    electrode_gap2 = gdspy.Rectangle((xs - ext/2 - loop/2 + inner_fillet/2,
                               ys - 1),
                              (xs - loop/2 + inner_fillet/2,
                               ys + 1))

    electrode_gap3 = gdspy.Rectangle((xs - loop/2 - padwidth/2 - 1,
                               ys + ext/2 - padwidth),
                              (xs - loop/2 - padwidth/2 + 1,
                               ys - padwidth))

    electrode_gap4 = gdspy.Rectangle((xs + loop/2 + padwidth/2 + 1,
                               ys + ext/2 - padwidth),
                              (xs + loop/2 + padwidth/2 - 1,
                               ys - padwidth))

    GND_pad = gdspy.Path(contactpadwidth, (xs, ys))
    GND_pad.segment(2*contactpadwidth, '+y')

    CPW_pad = gdspy.Path(contactpadwidth, (xs, ys - loop - padwidth))
    CPW_pad.segment(2*contactpadwidth, '-y')

    squidloop = gdspy.Path(padwidth, (xs, ys))
    squidloop.segment(side/2, '+x')
    squidloop.segment(side - inner_fillet, '-y')
    squidloop.turn(inner_fillet, "r")
    squidloop.segment(side - 2*inner_fillet, '-x')
    squidloop.turn(inner_fillet, "r")
    squidloop.segment(side - inner_fillet, '+y')
    squidloop.segment(side/2, '+x')

    squidloop = gdspy.boolean(squidloop, (GND_pad, CPW_pad), "or")
    squidloop = gdspy.boolean(squidloop, (jspace1, jspace2), "not")
    squidloop = squidloop.fillet(inner_fillet)
    squidloop = gdspy.boolean(squidloop, (electrode_gap1, electrode_gap2), "not")
    squidloop = gdspy.boolean(squidloop, (electrode_gap3, electrode_gap4), "not")
    squidloop.rotate(angle, (xs, ys))

    return looppatch, squidloop

# %%
# ===================================================================================
# SQUID JUNCTIONS DEFINITION
# ===================================================================================

def SQUID_Junctions(i, xs, ys, loop, junction, angle, num, device):
    if num == 2 or num == 1:
        v_left_electrode = gdspy.Path(junction, (xs - (loop+padwidth)/2, ys + ext))
        v_left_electrode.segment((inner_fillet + padwidth + ext)/2, '-y', layer=40)
        device.add(v_left_electrode.rotate(angle, (xs, ys)))                         # vertical left electrode

        v_left_patch = gdspy.Rectangle((xs - (loop+padwidth-2*patch_width)/2,
                                   ys - padwidth + (3*ext+1)/2),
                                  (xs - (loop+padwidth+2*patch_width)/2,
                                   ys - padwidth - ext), layer=50)
        v_left_patch = gdspy.PolygonSet.fillet(v_left_patch, inner_fillet/2)
        device.add(v_left_patch.rotate(angle, (xs, ys)))                             # vertical left patch


        h_left_electrode = gdspy.Path(junction, (xs - (loop+padwidth)/2 - ext, ys))
        h_left_electrode.segment((inner_fillet + padwidth + ext)/2, '+x', layer=40)
        device.add(h_left_electrode.rotate(angle, (xs, ys)))                         # horizontal left electrode

        h_left_patch = gdspy.Rectangle((xs - loop/2 - ext/2,
                                   ys + patch_width),
                                  (xs + 2*ext - loop/2 + ext/4,
                                   ys - patch_width), layer=50)
        h_left_patch = gdspy.PolygonSet.fillet(h_left_patch, inner_fillet/2)
        device.add(h_left_patch.rotate(angle, (xs, ys)))                             # horizontal left patch

    if num == 2 or num == 0:
        v_right_electrode = gdspy.Path(junction, (xs + (loop+padwidth)/2, ys + ext))
        v_right_electrode.segment((inner_fillet + padwidth + ext)/2, '-y', layer=40)
        device.add(v_right_electrode.rotate(angle, (xs, ys)))                        # vertical right electrode

        v_right_patch = gdspy.Rectangle((xs + (loop+padwidth-2*patch_width)/2,
                                   ys - padwidth + (3*ext+1)/2),
                                  (xs + (loop+padwidth+2*patch_width)/2,
                                   ys - padwidth - ext), layer=50)
        v_right_patch = gdspy.PolygonSet.fillet(v_right_patch, inner_fillet/2)
        device.add(v_right_patch.rotate(angle, (xs, ys)))                            # vertical right patch

        h_right_electrode = gdspy.Path(junction, (xs + (loop+padwidth)/2 + ext, ys))
        h_right_electrode.segment((inner_fillet + padwidth + ext)/2, '-x', layer=40)
        device.add(h_right_electrode.rotate(angle, (xs, ys)))                        # horizontal right electrode

        h_right_patch = gdspy.Rectangle((xs + loop/2 + ext/2,
                                   ys + patch_width),
                                  (xs - 2*ext + loop/2 - ext/4,
                                   ys - patch_width), layer=50)
        h_right_patch = gdspy.PolygonSet.fillet(h_right_patch, inner_fillet/2)
        device.add(h_right_patch.rotate(angle, (xs, ys)))                            # horizontal right patch

# %%
# ===================================================================================
# MY TEST JUNCTION DEFINITION
# ===================================================================================

def mytestSQUID(xs, ys, loop, junction, num, layer, dt, device, noholesarea):
    cpw = gdslib.CPWPath(my_padx, 25, layer, datatype=dt, cellName=device)
    cpw.start([xs, ys], '-y')
    cpw.openGap(25)
    cpw.straight(my_pady)
    cpw.openGap(loop + 25)
    cpw.straight(my_pady)
    cpw.openGap(25)

    tSQUID = cpw.makePolySet(cpw.path)

    squidloop = SQUID_Loop(0, xs, ys - loop - my_pady,
                           loop, junction, 0, num, device)

    tSQUID = gdspy.boolean(tSQUID, squidloop[1], "not", layer=layer, datatype=dt)
    SQUID_Junctions(0, xs, ys - my_pady - loop, loop, junction, 0, num, device)

    notch1 = gdspy.Rectangle((xs-10, ys-10),
                             (xs+10, ys-20-my_pady))
    notch2 = gdspy.Rectangle((xs-10, ys-my_pady-loop - 55),
                             (xs+10, ys-2*my_pady-loop-50))
    tSQUID = gdspy.boolean(tSQUID, (notch1, notch2), "or", layer=layer, datatype=dt)

    outer = gdspy.offset(tSQUID, cheesing_offset, join_first=False, layer=13)
    inner = gdspy.Rectangle(
        (xs - my_pady/2,
         ys - 25),
        (xs + my_pady/2,
         ys - 50 - 2*my_padx - loop),
        layer=13)

    geo_offset = gdspy.boolean(outer, inner, "or", layer=13)
    noholes = gdspy.boolean(noholesarea, geo_offset, "or", layer=13)

    return tSQUID, noholes

# %%
# ===================================================================================
# STANDARD TEST JUNCTION DEFINITION
# ===================================================================================

def stdtestSQUID(xs, ys, loop, junction, num, layer, dt, device, noholesarea):
    cpw = gdslib.CPWPath(std_padx, 25, layer, datatype=dt, cellName=device)
    cpw.start([xs, ys], '-y')
    cpw.openGap(25)
    cpw.straight(std_pady)
    cpw.openGap(loop + 25)
    cpw.straight(std_pady)
    cpw.openGap(25)

    tSQUID = cpw.makePolySet(cpw.path)

    squidloop = SQUID_Loop(0, xs, ys - loop - std_pady,
                           loop, junction, 0, num, device)

    tSQUID = gdspy.boolean(tSQUID, squidloop[1], "not", layer=layer, datatype=dt)
    SQUID_Junctions(0, xs, ys - std_pady - loop, loop, junction, 0, num, device)

    notch1 = gdspy.Rectangle((xs-25, ys-25), (xs+25, ys-std_pady))
    notch2 = gdspy.Rectangle((xs-25, ys-std_pady-loop-75), (xs+25, ys-2*std_pady-loop-50))
    tSQUID = gdspy.boolean(tSQUID, (notch1, notch2), "or", layer=layer, datatype=dt)

    outer = gdspy.offset(tSQUID, cheesing_offset, join_first=False, layer=13)
    inner = gdspy.Rectangle(
        (xs - std_pady/2,
         ys - 25),
        (xs + std_pady/2,
         ys - 50 - 2*std_padx - loop),
        layer=13)

    geo_offset = gdspy.boolean(outer, inner, "or", layer=13)
    noholes = gdspy.boolean(noholesarea, geo_offset, "or", layer=13)

    return tSQUID, noholes

# %%
# ===================================================================================
# AIR BRIDGE DEFINITION
# ===================================================================================

def airbridge(pos_x, pos_y, device):
    # ===============================================================================
    # AIR BRIDGE CONTACT PADS
    # ===============================================================================

    device.add(gdspy.Rectangle(
        (pos_x + 5, pos_y - 2),
        (pos_x + bridgepad_x + 5, pos_y - bridgepad_y - 2),
        layer=60))                                                                   # TL pad

    device.add(gdspy.Rectangle(
        (pos_x + 5, pos_y + 42),
        (pos_x + bridgepad_x + 5, pos_y - bridgepad_y + 42),
        layer=60))                                                                   # FL pad

    # ===============================================================================
    # AIR BRIDGE PADS
    # ===============================================================================

    device.add(gdspy.Rectangle(
        (pos_x + 6, pos_y - 3),
        (pos_x + 6 + bridge_x, pos_y - bridge_y - 3),
        layer=61))                                                                   # TL pad
    device.add(gdspy.Rectangle(
        (pos_x + 6, pos_y + 41),
        (pos_x + 6 + bridge_x, pos_y - bridge_y + 41),
        layer=61))                                                                   # FL pad

    # ===============================================================================
    # AIR BRIDGES
    # ===============================================================================

    device.add(gdspy.Rectangle(
        (pos_x + 3 + 5, pos_y - 11 + 3 + 5),
        (pos_x + 3 + 5 + 14, pos_y - 11 + 44),
        layer=61))                                                                   # air bridge

# %%
# ===================================================================================
# IN-PLANE LOOP DEFINITION
# ===================================================================================

def Transfer_Loop(xs, ys, loop, device):

    TL_x = xs - loop/2 - padwidth/2 + 2*gap
    TL_y = ys - gap - width
    side = loop - 2*gap - width - fillet

    startpad = gdspy.Rectangle((TL_x - 2.5, TL_y + 1.5),
                               (TL_x + padsize + 2.5, TL_y - 2*padsize/3 + 1.5))

    path = gdspy.Path(width, (TL_x, TL_y))
    path.segment(side, "-y")
    path.turn(fillet, "l")

    if side - fillet > 1:
        path.segment(side - fillet, "+x")
    else:
        path.segment(1, '+x')

    path.turn(fillet, "l")

    if side - fillet > 1:
        path.segment(side - fillet, "+y")
    else:
        path.segment(1, '+y')

    path.turn(fillet, "l")

    if side - 2*padsize - 10 > 1:
        path.segment(side - 2*padsize - 10, "-x")
    else:
        path.segment(1, '-x')

    loop_path = gdspy.boolean(path, None, "or", max_points=0)

    endpad = gdspy.Rectangle((TL_x + 2.5*padsize + 12.5, TL_y + width/2),
                             (TL_x + 1.5*padsize + 7.5, TL_y + width/2 - 2*padsize/3))

    TL = gdspy.boolean((startpad, endpad), loop_path, "or")

    airbridge(TL_x, TL_y, device)
    airbridge(TL_x+ 1.5*padsize + 10, TL_y+ width/2 - 2.5, device)

    return TL

# ===================================================================================
# IN-PLANE FLUX LINES
# ===================================================================================

def fluxline(x, y, xlen1, xlen2, ylen1, device, noholesarea):
    cpwloop1 = gdslib.CPWPath(padsize, 10, layer=10, cellName=device)
    cpwloop1.start([x, y], '+y')
    cpwloop1.openGap(5)
    cpwloop1.straight(padsize)
    cpwloop1.straight(20, 5, 2)
    cpwloop1.straight(5)
    cpwloop1.bend(5, -pi/2)
    cpwloop1.straight(12)
    cpwloop1.bend(5, pi/2)
    cpwloop1.straight(ylen1)

    cpwloop1.bend(20, pi/2)
    cpwloop1.straight(xlen1)
    cpwloop1.bend(20, -pi/2)
    cpwloop1.straight(xlen2)

    cpwloop1.straight(150, 150, 30)
    cpwloop1.straight(150)
    cpwloop1.openGap(30)
    cpwloop1.end()

    cpwloop2 = gdslib.CPWPath(padsize, 10, layer=10, cellName=device)
    cpwloop2.start([x+55, y], '+y')
    cpwloop2.openGap(5)
    cpwloop2.straight(padsize)
    cpwloop2.straight(20, 5, 2)
    cpwloop2.straight(5)
    cpwloop2.bend(5, pi/2)
    cpwloop2.straight(12)
    cpwloop2.bend(5, -pi/2)
    cpwloop2.straight(ylen1)


    cpwloop2.bend(20, -pi/2)
    cpwloop2.straight(xlen1)
    cpwloop2.bend(20, pi/2)
    cpwloop2.straight(xlen2)

    cpwloop2.straight(150, 150, 30)
    cpwloop2.straight(150)
    cpwloop2.openGap(30)
    cpwloop2.end()

    loopfeed1 = gdspy.boolean(
        cpwloop1.makePolySet(cpwloop1.path),
        cpwloop1.makePolySet(cpwloop2.path), "or")

    loopfeed2 = cpwloop2.makePolySet(cpwloop1.path)

    flpad1 = gdspy.Rectangle((x-130-xlen2, y+130+ylen1+padsize), (x-xlen2,y+380+ylen1+padsize),layer=13)
    flpad2 = gdspy.Rectangle((x-xlen2+60, y+130+ylen1+padsize), (x-xlen2+190,y+380+ylen1+padsize),layer=13)

    outer = gdspy.offset(loopfeed1, cheesing_offset+5, join_first=False, layer=13)
    inner = gdspy.offset(loopfeed2, cheesing_offset+5, join_first=False, layer=13)
    geo_offset = gdspy.boolean((outer, inner),(flpad1, flpad2), "or", layer=13)
    noholes = gdspy.boolean(noholesarea, geo_offset, "or", layer=13)

    return loopfeed1, noholes

# %%
# ===================================================================================
# FLIP CHIP CONNECTION AND CONTACT PAD DEFINITION
# ===================================================================================

def connection_pad(x, y, sizex, sizey, layer, dt, device):
    cpw = gdslib.CPWPath(3*Feed_pad, 100,
                         layer=layer, datatype=dt, cellName=device)
    cpw.start((x, y), '+x')
    cpw.openGap(100)
    cpw.straight(2*Feed_pad)
    cpw.straight(Feed_pad, widthEnd=100, gapEnd=100)
    cpw.straight(Feed_pad/2)

    cpw1 = gdslib.CPWPath(100, sizey/2+padoffset-100/2,
                          layer=layer, datatype=dt, cellName=device)
    cpw1.start((x+3*Feed_pad+100, y), '+x')
    cpw1.straight(padoffset)

    cpw2 = gdslib.CPWPath(sizey, padoffset, layer=layer,  datatype=dt, cellName=device)
    cpw2.start((x+3*Feed_pad+padoffset+100, y), '+x')
    cpw2.straight(sizex)
    cpw2.openGap(padoffset)

    merged_path = []
    merged_path.append(cpw.path)
    merged_path.append(cpw1.path)
    merged_path.append(cpw2.path)

    return merged_path


def contact_pad(x, y, sizex, sizey, layer, dt, device):
    cpw = gdslib.CPWPath(sizey, padoffset, layer=layer,  datatype=dt, cellName=device)
    cpw.start((x+3*Feed_pad+padfeed-100, y), '+x')
    cpw.openGap(padoffset)
    cpw.straight(sizex)
    cpw.openGap(padoffset)
    cpw.end()

    return cpw.path

# %%
# ===================================================================================
# FLIP CHIP INPUT COIL
# ===================================================================================

def FCline(xf, yf, xs, ys, loop, coil, device):
    FCline = gdspy.Path(wirewidth, (xf, yf))

    FCline.segment(xs - xf - 25,
                   '+x', layer=6)
    FCline.turn(10, 'r', layer=6)

    FCline.segment(yf - ys - coil/2 - 22.5,
                   '-y', layer=6)
    FCline.turn(10, 'r', layer=6)

    if coil/2-30 > 1:
        FCline.segment(coil/2-30, '-x', layer=6)
    else:
        FCline.segment(1, '-x', layer=6)

    FCline.turn(10, 'l', layer=6)

    if coil-10 > 1:
        FCline.segment(coil-10, '-y', layer=6)
    else:
        FCline.segment(1, '-y', layer=6)

    FCline.turn(10, 'l', layer=6)

    if coil-10 > 1:
        FCline.segment(coil-10, '+x', layer=6)
    else:
        FCline.segment(1, '+x', layer=6)

    FCline.turn(10, 'l', layer=6)

    if coil-10 > 1:
        FCline.segment(coil-10, '+y', layer=6)
    else:
        FCline.segment(1, '+y', layer=6)
    FCline.turn(10, 'l', layer=6)

    if coil/2-30 > 1:
        FCline.segment(coil/2-30, '-x', layer=6)
    else:
        FCline.segment(1, '-x', layer=6)

    FCline.turn(10, 'r', layer=6)

    FCline.segment(yf - ys - coil/2 - 22.5,
                   '+y', layer=6)
    FCline.turn(10, 'r', layer=6)

    FCline.segment(xs - xf - 25,
                   '+x', layer=6)
    return FCline

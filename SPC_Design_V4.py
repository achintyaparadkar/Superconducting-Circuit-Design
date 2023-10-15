# %%
# ===================================================================================
# IMPORT LIBRARIES AND LAYOUTS
# ===================================================================================
import gdspy
from numpy import pi
from SPCV4_Definitions import *
from MyLibrary import EBLmarker, FCmarker, feedline1, feedline2, CPW_Res, CPW_SQUID
from MyLibrary import SQUID_Loop, SQUID_Junctions, mytestSQUID, stdtestSQUID, airbridge
from MyLibrary import FCline, Transfer_Loop, fluxline, connection_pad, contact_pad

gdspy.current_library = gdspy.GdsLibrary()
lib = gdspy.GdsLibrary()
devicelist = []

logocell = gdspy.GdsLibrary(name='MPW002', infile='C:/Users/achintya/'
                            'OneDrive - Chalmers/Documents/1. Project/'
                            '6. Python Scripts/svg2gdsii/nazca_export.gds',
                            unit=1e-06, precision=1e-09).extract(
    'SuperMeQ2v1.jpg', overwrite_duplicate=True)
logo = gdspy.CellReference(logocell,
                           origin=(300, 2800), magnification=(1), rotation=90)

infra = gdspy.GdsLibrary(name='MPW002', infile='C:/Users/achintya/'
                         'OneDrive - Chalmers/Documents/1. Project/'
                         '5. Coupling Project/Chip Design/Wafer Infrastructure.gds',
                         unit=1e-06, precision=1e-09)
wafer = infra.extract('MPW002', overwrite_duplicate=False)

# %%
for nofluxline in range(0, 2):
    for junc_count in range(0, 4):
        for loop_count in range(0, 2):
            for Qc_count in range(0, 2):

                # ===========================================================================
                # CHIP
                # ===========================================================================
                loop = [100*(1+loop_count), 20]

                deviceName = str(loop[0]) \
                             +'x'+"{:.1f}".format(0.3+0.1*junc_count) \
                             +'x'+str(Qc[Qc_count]) \
                             +'x'+str(nofluxline)
                device = lib.new_cell(deviceName)

                chip = gdspy.Rectangle((0, 0), (Chip_width, Chip_height), layer=0)
                device.add(chip)

                FCchip = gdspy.Rectangle(
                    ((Chip_width-FC_Chip_width)/2,
                     (Chip_height-FC_Chip_height)/2),
                    ((Chip_width-FC_Chip_width)/2+FC_Chip_width,
                     (Chip_height-FC_Chip_height)/2+FC_Chip_height), layer=1)
                device.add(FCchip)

                device.add(logo)

                global noholes
                noholes = gdspy.offset(logo, cheesing_offset+10,
                                       join_first=True, layer=13)

                # %%
                # ===========================================================================
                # FEEDLINE
                # ===========================================================================
                feed = feedline2(Feed_x, Feed_y, 10, 1, device, noholes)
                device.add(feed[0])
                noholes = feed[1]
                yres = feed[2]

                # %%
                # ===========================================================================
                # RESONATOR ARRAY
                # ===========================================================================
                xs = []
                ys = []

                for i in range(0, 1):
                    xr = xres[i]
                    yr = yres + C_gap0[Qc_count] + CWt/2 + CGt + CW[i]/2 + CG[i]
                    reslen = length[junc_count][Qc_count][i]

                    res = CPW_Res(i, xr, yr, reslen, 10, 2, device, noholes)
                    device.add(res[0])
                    noholes = res[1]

                for i in range(1, 3):
                    xr = xres[i]
                    yr = yres + C_gap[loop_count][i-1][Qc_count] + CWt/2 + CGt + CW[i]/2 + CG[i]
                    reslen = length[junc_count][loop_count][i]

                    if i == 1 and nofluxline == 0:
                        res = CPW_SQUID(i, xr, yr, reslen, loop[i-1], 0.3+0.1*junc_count,
                                        10, 3, device, noholes)
                        noholes = res[1]
                        xs.append(res[2])
                        ys.append(res[3])

                        TL = Transfer_Loop(xs[i-1], ys[i-1], loop[i-1], device)
                        fluxline(xs[i-1]-loop[i-1]/2+22.5, ys[i-1]+10,
                                 50, 5, 3650-ys[i-1], device, noholes)[0]
                        noholes = fluxline(xs[i-1]-loop[i-1]/2+22.5, ys[i-1]+10,
                                 50, 5, 3650-ys[i-1], device, noholes)[1]

                        res_coupled = gdspy.boolean(res[0], TL, "not", layer=10, datatype=3)
                        device.add(res_coupled)

                    else:
                        res = CPW_SQUID(i, xr, yr, reslen, loop[i-1], 0.3+0.1*junc_count,
                                        10, 3, device, noholes)
                        noholes = res[1]
                        xs.append(res[2])
                        ys.append(res[3])

                        device.add(res[0])

                # %%
                # ===========================================================================
                # FTR FLIP CHIP PADS
                # ===========================================================================
                mainpad1 = connection_pad(posx1, posy2, padsizex, padsizey, 10, 8, device)
                device.add(mainpad1)

                mainpad2 = []
                for path in mainpad1:
                    polygons = gdspy.PolygonSet(path.polygons, layer=10, datatype=8)
                    mirrored_polygons = polygons.mirror((Chip_width/2, 0),
                                                        (Chip_width/2, Chip_height))
                    mainpad2.append(mirrored_polygons)
                device.add(mainpad2)

                mainpad3 = contact_pad(posx1, posy1, padsizex, padsizey, 10, 8, device)
                device.add(mainpad3)

                polygons = gdspy.PolygonSet(mainpad3.polygons, layer=10, datatype=8)
                mainpad4 = polygons.mirror((Chip_width/2, 0), (Chip_width/2, Chip_height))
                device.add(mainpad4)

                geo_offset = gdspy.offset(mainpad1, cheesing_offset+10, datatype=8,
                                          join_first=False, layer=13)
                block1 = gdspy.Polygon(((posx1+100, posy2-3*Feed_pad/2),
                                (posx1+100+2*Feed_pad, posy2-3*Feed_pad/2),
                                (posx1+100+3*Feed_pad, posy2-100/2),
                                (posx1+100+3*Feed_pad+padoffset, posy2-100/2),
                                (posx1+100+3*Feed_pad+padoffset, posy2-padsizey/2),
                                (posx1+100+3*Feed_pad+padoffset+padsizex, posy2-padsizey/2),
                                (posx1+100+3*Feed_pad+padoffset+padsizex, posy2+padsizey/2),
                                (posx1+100+3*Feed_pad+padoffset, posy2+padsizey/2),
                                (posx1+100+3*Feed_pad+padoffset, posy2+100/2),
                                (posx1+100+3*Feed_pad, posy2+100/2),
                                (posx1+100+2*Feed_pad, posy2+3*Feed_pad/2),
                                (posx1+100, posy2+3*Feed_pad/2)))
                noholes = gdspy.boolean((noholes, geo_offset), block1, "or", layer=13)

                geo_offset = gdspy.offset(mainpad2, cheesing_offset+10, datatype=8,
                                          join_first=False, layer=13)
                polygons = gdspy.PolygonSet(block1.polygons, layer=11, datatype=8)
                block2 = polygons.mirror((Chip_width/2, 0), (Chip_width/2, Chip_height))

                noholes = gdspy.boolean((noholes, geo_offset), block2, "or", layer=13)

                geo_offset = gdspy.offset(mainpad3, cheesing_offset,
                                          join_first=False, layer=13)
                noholes = gdspy.boolean((noholes, geo_offset),
                    gdspy.Rectangle((posx1+100+3*Feed_pad+padoffset,
                                     posy1-padsizey/2),
                                    (posx1+100+3*Feed_pad+padoffset+padsizex,
                                     posy1+padsizey/2)), "or", layer=13)

                geo_offset = gdspy.offset(mainpad4, cheesing_offset,
                                          join_first=False, layer=13)
                noholes = gdspy.boolean((noholes, geo_offset),
                    gdspy.Rectangle((posx2-100-3*Feed_pad-padoffset,
                                     posy1-padsizey/2),
                                    (posx2-100-3*Feed_pad-padoffset-padsizex,
                                     posy1+padsizey/2)), "or", layer=13)

                # %%
                # ===========================================================================
                # FC FLIP CHIP PADS
                # ===========================================================================
                FCpad1 = gdspy.Rectangle((posx1+3*Feed_pad+padoffset+100,
                                          posy2-padsizey/2),
                                         (posx1+3*Feed_pad+padoffset+100+padsizex+500,
                                          posy2+padsizey/2),
                                         layer=7, datatype=1)

                FCpad2 = gdspy.Rectangle((posx2-3*Feed_pad-padoffset-100-padsizex-470,
                                          posy2-padsizey/2),
                                         (posx2-3*Feed_pad-padoffset-100,
                                          posy2+padsizey/2),
                                         layer=7, datatype=1)

                FCpad3 = gdspy.Rectangle((posx1+3*Feed_pad+padoffset+100,
                                          posy1-padsizey/2),
                                         (posx1+3*Feed_pad+padoffset+100+padsizex,
                                          posy1+padsizey/2),
                                         layer=7, datatype=1)

                FCpad4 = gdspy.Rectangle((posx2-3*Feed_pad-padoffset-100-padsizex,
                                          posy1-padsizey/2),
                                         (posx2-3*Feed_pad-padoffset-100,
                                          posy1+padsizey/2),
                                         layer=7, datatype=1)

                device.add(FCpad1)
                device.add(FCpad2)
                device.add(FCpad3)
                device.add(FCpad4)

                # %%
                # ===========================================================================
                # FLUX LINES AND INPUT COIL
                # ===========================================================================

                t = 0
                xf = posx1+3*Feed_pad+padoffset+100+padsizex
                yf = posy2-padsizey/2 + 100

                FC_line = FCline(xf, yf, xs[t], ys[t]-loop[t]/2, loop[t],
                                 coil[Qc_count], device)
                #FC_line = FC_line.mirror((3500,5000), (3500,0))
                device.add(FC_line)

                # %%
                # ===========================================================================
                # TEST JUNCTIONS
                # ===========================================================================
                for j in range(0, 10):

                    if j<5:
                        my_TJstartx = 450
                    else:
                        my_TJstartx = 4550

                    for k in range(0, 2):
                        testloop = 30
                        junct = 0.05 + 0.05 * k + (0.1*j)

                        x_clearance = (my_padx+2*25+my_TJclearance)*j
                        y_clearance = (2*(my_pady+2*25)+my_TJclearance)*k

                        test_x = my_TJstartx + x_clearance
                        test_y = my_TJstarty + y_clearance + testloop

                        tSQUID = mytestSQUID(test_x, test_y, testloop, junct, 2,
                                           10, 4, device, noholes)

                        device.add(tSQUID[0])
                        noholes = tSQUID[1]

                # %%
                # ===========================================================================
                # DICING MARKERS - FLIP-CHIP
                # ===========================================================================
                for j in range(0, 2):
                    for k in range(0, 2):
                        xpos = (Chip_width-FC_Chip_width)/2 + (FC_Chip_width+20) * j
                        ypos = (Chip_height-FC_Chip_height)/2 + (FC_Chip_height+20) * k

                        FC_dicing_marker = EBLmarker(xpos, ypos,
                                                     markersize, markergap, extension, 6, 1)
                        device.add(FC_dicing_marker)

                # %%
                # ===========================================================================
                # ALIGNMENT MARKERS - FTR CHIP
                # ===========================================================================
                for j in range(0, 2):
                    for k in range(0, 2):
                        xpos = 160 + (Chip_width-300) * j
                        ypos = 160 + (Chip_height-300) * k

                        FTR_dicing_marker = EBLmarker(xpos, ypos,
                                                      markersize, markergap, extension, 10, 5)
                        device.add(FTR_dicing_marker)

                        geo_offset = gdspy.offset(FTR_dicing_marker, cheesing_offset/2,
                                                  join_first=False, layer=13)
                        noholes = gdspy.boolean(noholes, geo_offset,
                                                "or", layer=13)

                # ===========================================================================
                # ALIGNMENT MARKERS - FLIP-CHIP
                # ===========================================================================

                for j in range(0, 1):
                    for k in range(0, 2):
                        xpos = Chip_width/2
                        ypos = 750 + 3500 * k

                        FC_align_marker = EBLmarker(xpos+20, ypos+20,
                                                    markersize, markergap, extension, 6, 1)
                        device.add(FC_align_marker)

                        FTR_align_marker = FCmarker(xpos, ypos,
                                                    markersize, markergap, extension, 10, 6)
                        device.add(FTR_align_marker)

                        geo_offset = gdspy.offset(FTR_align_marker, cheesing_offset/2,
                                                  join_first=False, layer=13)
                        noholes = gdspy.boolean(noholes, geo_offset,
                                                "or", layer=13)

                # %%
                # ===========================================================================
                # DEVICE LABELS
                # ===========================================================================

                Text1 = gdspy.Text('SPC-V3', 150, (5800, 3200),
                                   layer=10, datatype=7)
                Text2 = gdspy.Text("{:.1f}".format(0.3+0.1*junc_count), 300, (5800, 2800),
                                   layer=10, datatype=7)
                Text3 = gdspy.Text(str(loop[0]), 400, (5800, 2350),
                                   layer=10, datatype=7)
                Text4 = gdspy.Text(str(int(Qc[Qc_count]/1000))+'k', 300, (5800, 2100),
                                   layer=10, datatype=7)
                Text5 = gdspy.Text(str(coil[Qc_count]), 400, (3250, 2200), angle=pi/2,
                                   layer=6, datatype=2)
                Text6 = gdspy.Text('^'+str(loop[0]), 400, (4300, 1800), angle=pi/2,
                                   layer=6, datatype=2)

                device.add(Text1)
                device.add(Text2)
                device.add(Text3)
                device.add(Text4)
                device.add(Text5)
                device.add(Text6)

                geo_offset = gdspy.offset(
                    gdspy.fast_boolean({Text1, Text2, Text3}, Text4, "or"),
                    cheesing_offset+50,
                    join_first=True, layer=13)
                noholes = gdspy.boolean(noholes, geo_offset,
                                        "or", layer=13)

                for i in range(0, 10):  # Test SQUID
                    if i<5:
                        my_TJstartx = 400
                    else:
                        my_TJstartx = 4550

                    Text5 = gdspy.Text(str(int(round(50+100*i, 0))), 50,
                                       (my_TJstartx + (my_padx+3*my_TJclearance)*i,
                                        my_TJstarty - 3*my_pady), layer=10, datatype=7)
                    device.add(Text5)

                    geo_offset = gdspy.offset(Text5, cheesing_offset/2,
                                              join_first=False, layer=13)
                    noholes = gdspy.boolean(noholes, geo_offset,
                                            "or", layer=13)

                    Text6 = gdspy.Text(str(int(round(100+100*i, 0))), 50,
                                       (my_TJstartx + (my_padx+3*my_TJclearance)*i,
                                        my_TJstarty + 3*my_pady),
                                       layer=10, datatype=7)
                    device.add(Text6)
                    geo_offset = gdspy.offset(Text6, cheesing_offset/2,
                                              join_first=False, layer=13)
                    noholes = gdspy.boolean(noholes, geo_offset,
                                            "or", layer=13)
                noholes = gdspy.fast_boolean(chip, noholes,
                                             "not", layer=13)

                # %%
                # ===========================================================================
                # WAFER CHEESING HOLES
                # ===========================================================================
                x_hole = 8
                y_hole = 8
                hole_width = 2
                hole_height = 2

                x = x_hole + hole_width
                y = y_hole + hole_height

                for i in range(0, int(Chip_width / (x_hole + hole_width))):
                    for j in range(0, int(Chip_height / (y_hole + hole_height))):
                        hole = gdspy.Rectangle(
                            (0 + i * x, 0 + j * y),
                            (hole_width + i * x, hole_width + j * y),
                            layer=14)
                        device.add(hole)

                holes = device.get_polygons(by_spec=True)[(14, 0)]

                cheese = gdspy.boolean(holes, noholes, 'and', layer=10, datatype=10)
                device.add(cheese)

                def remove_layer(poly, layer, datatype):
                    return layer == 14
                device.remove_polygons(remove_layer)

                devicelist.append(str(deviceName))
                gdspy.write_gds('C:/Users/achintya/OneDrive - Chalmers/Documents/'
                                '1. Project/6. Python Scripts/SQUID Cavity/GDSPY Script/'
                                'SPC Design V4 - Separate Chips/'+deviceName+'.gds',
                                cells=[deviceName, logocell])

# %%
# ===========================================================================
# STANDARD TEST JUNCTIONS CHIPS
# ===========================================================================
testchip = lib.new_cell("testchip")
testchip.add(gdspy.Rectangle((0, 0), (Chip_width, Chip_height), layer=0))

for i in range(0, 2):
    for j in range(0, 10):
        for k in range(0, 2):
            testloop = 30
            junct = 0.05 + (0.01+0.015*i)*k + (0.02+0.03*i)*j + 0.2*i

            x_clearance = (std_padx+2*25+std_TJclearance)*j
            y_clearance = (2*(std_pady+2*25)+std_TJclearance)*k

            test_x = std_TJstartx + x_clearance
            test_y = std_TJstarty + y_clearance + testloop + 1500*i

            tSQUID = stdtestSQUID(test_x, test_y, testloop, junct, 2,
                               10, 4, testchip, noholes)

            testchip.add(tSQUID[0])

    for j in range(0, 10):  # Test SQUID

        Text5 = gdspy.Text(str(int(round(50+(20+30*i)*j+200*i, 0))), 50,
                           (std_TJstartx + (std_padx+2*std_TJclearance)*j,
                            std_TJstarty + 1500*i - 3*std_pady), layer=10, datatype=7)
        testchip.add(Text5)

        Text6 = gdspy.Text(str(int(round((60+15*i)+(20+30*i)*j+200*i, 0))), 50,
                           (std_TJstartx + (std_padx+2*std_TJclearance)*j,
                            std_TJstarty + 1500*i + 3*std_pady+25),
                           layer=10, datatype=7)
        testchip.add(Text6)

for j in range(0, 2):
    for k in range(0, 2):
        xpos = 160 + (Chip_width-300) * j
        ypos = 160 + (Chip_height-300) * k

        FTR_dicing_marker = EBLmarker(xpos, ypos,
                                      markersize, markergap, extension, 10, 5)
        testchip.add(FTR_dicing_marker)

# %%
# ===================================================================================
# WAFER LAYOUT
# ===================================================================================
wafer_x = 0
wafer_y = 0
chiprow = [6, 8, 8, 8, 6]
chipcol = 6

x_offset = 5
y_offset = -3500
chipgap = 10

j = 0

# for i in range(0, len(devicelist)+4):
#     if wafer_x < chiprow[wafer_y]:

#         wafer.add(gdspy.CellReference(
#             lib.extract(devicelist[(i-j) % len(devicelist)]), origin=(
#                 -(Chip_height+chipgap)*chiprow[wafer_y]/2
#                 + (Chip_height+chipgap)*wafer_x,
#                 +(Chip_width+chipgap)*chipcol/2
#                 - (Chip_width+chipgap)*wafer_y + y_offset),
#             rotation=-90))

#         wafer.add(gdspy.CellReference(
#             infra.extract('Dicing'), origin=(
#                 -(Chip_height+chipgap) * chiprow[wafer_y] / 2
#                 + (Chip_height+chipgap) * wafer_x - 5,
#                 +(Chip_width+chipgap) * chipcol / 2
#                 - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

#         wafer_x = wafer_x + 1

#     else:

#         wafer_x = 0
#         wafer_y = wafer_y + 1

#         wafer.add(gdspy.CellReference(
#             lib.extract(devicelist[(i-j) % len(devicelist)]), origin=(
#                 -(Chip_height+chipgap)*chiprow[wafer_y]/2
#                 + (Chip_height+chipgap)*wafer_x,
#                 +(Chip_width+chipgap)*chipcol/2
#                 - (Chip_width+chipgap)*wafer_y + y_offset),
#             rotation=-90))

#         wafer.add(gdspy.CellReference(
#             infra.extract('Dicing'), origin=(
#                 -(Chip_height+chipgap) * chiprow[wafer_y] / 2
#                 + (Chip_height+chipgap) * wafer_x - 5,
#                 +(Chip_width+chipgap) * chipcol / 2
#                 - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

#         wafer_x = wafer_x + 1

for i in range(0, len(devicelist)+4):
    if (i+1)%6==0:
        if wafer_x < chiprow[wafer_y]:

            wafer.add(gdspy.CellReference(
                lib.extract("testchip"), origin=(
                    -(Chip_height+chipgap)*chiprow[wafer_y]/2
                    + (Chip_height+chipgap)*wafer_x,
                    +(Chip_width+chipgap)*chipcol/2
                    - (Chip_width+chipgap)*wafer_y + y_offset),
                rotation=-90))

            wafer.add(gdspy.CellReference(
                infra.extract('Dicing'), origin=(
                    -(Chip_height+chipgap) * chiprow[wafer_y] / 2
                    + (Chip_height+chipgap) * wafer_x - 5,
                    +(Chip_width+chipgap) * chipcol / 2
                    - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

            wafer_x = wafer_x + 1

        else:

            wafer_x = 0
            wafer_y = wafer_y + 1

            wafer.add(gdspy.CellReference(
                lib.extract("testchip"), origin=(
                    -(Chip_height+chipgap)*chiprow[wafer_y]/2
                    + (Chip_height+chipgap)*wafer_x,
                    +(Chip_width+chipgap)*chipcol/2
                    - (Chip_width+chipgap)*wafer_y + y_offset),
                rotation=-90))

            wafer.add(gdspy.CellReference(
                infra.extract('Dicing'), origin=(
                    -(Chip_height+chipgap) * chiprow[wafer_y] / 2
                    + (Chip_height+chipgap) * wafer_x - 5,
                    +(Chip_width+chipgap) * chipcol / 2
                    - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

            wafer_x = wafer_x + 1
        j = j+1

    else:
        if wafer_x < chiprow[wafer_y]:

            wafer.add(gdspy.CellReference(
                lib.extract(devicelist[(i-j) % len(devicelist)]), origin=(
                    -(Chip_height+chipgap)*chiprow[wafer_y]/2
                    + (Chip_height+chipgap)*wafer_x,
                    +(Chip_width+chipgap)*chipcol/2
                    - (Chip_width+chipgap)*wafer_y + y_offset),
                rotation=-90))

            wafer.add(gdspy.CellReference(
                infra.extract('Dicing'), origin=(
                    -(Chip_height+chipgap) * chiprow[wafer_y] / 2
                    + (Chip_height+chipgap) * wafer_x - 5,
                    +(Chip_width+chipgap) * chipcol / 2
                    - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

            wafer_x = wafer_x + 1

        else:

            wafer_x = 0
            wafer_y = wafer_y + 1

            wafer.add(gdspy.CellReference(
                lib.extract(devicelist[(i-j) % len(devicelist)]), origin=(
                    -(Chip_height+chipgap)*chiprow[wafer_y]/2
                    + (Chip_height+chipgap)*wafer_x,
                    +(Chip_width+chipgap)*chipcol/2
                    - (Chip_width+chipgap)*wafer_y + y_offset),
                rotation=-90))

            wafer.add(gdspy.CellReference(
                infra.extract('Dicing'), origin=(
                    -(Chip_height+chipgap) * chiprow[wafer_y] / 2
                    + (Chip_height+chipgap) * wafer_x - 5,
                    +(Chip_width+chipgap) * chipcol / 2
                    - (Chip_width+chipgap) * wafer_y + y_offset + 5)))

            wafer_x = wafer_x + 1

# blank = wafer.get_polygons(by_spec=True)[(6, 0)]

# inverted_layer = gdspy.fast_boolean(outer_disc, blank, 'not', layer = 7)
# wafer.add(inverted_layer)

# %%
# ===================================================================================
# PRINT LAYOUT
# ===================================================================================
lib.top_level()
gdspy.write_gds('C:/Users/achintya/OneDrive - Chalmers/Documents/1. Project/'
                '6. Python Scripts/SQUID Cavity/GDSPY Script/SPC_Design_V4.gds',
                cells=None, name='library', unit=1.0e-6, precision=1.0e-9)

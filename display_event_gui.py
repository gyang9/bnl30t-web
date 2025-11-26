
import uproot
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import sys


def data_for_cylinder_along_z(center_x,center_y,radius,height_z):
    z = np.linspace(-height_z, height_z, 50)
    theta = np.linspace(0, 2*np.pi, 50)
    theta_grid, z_grid=np.meshgrid(theta, z)
    x_grid = radius*np.cos(theta_grid) + center_x
    y_grid = radius*np.sin(theta_grid) + center_y
    return x_grid,y_grid,z_grid

def display_charge(chg, hchg, atime, ievt, isavefig, fig, ax1, ax2, ax3d):
    dis_x=[]
    dis_y=[]
    area=[]
    area2=[]
    area3=[]
    colo=[]
    colo2=[]
    colo3 = []
    locx_bot = [508.000, 285.800, 769.900, 0.000, -317.500, -879.900, -698.500, -934.900, -381.000, 0.000, 412.800, 1044.900
               ]
    locy_bot = [0.000, 494.900, 444.500, 952.500, 549.900, 508.000, 0.000, -539.800, -659.900, -1143.000, -714.900, -603.300]
    locx_side= [-1133.5, -1133.5, -1133.5, -1133.5, -566.75, -566.75, -566.75, -566.75, 566.75, 566.75, 566.75, 566.75, 1133.5, 1133.5, 1133.5, 1133.5, 566.75, 566.75, 566.75, 566.75, -566.75, -566.75, -566.75, -566.75]
    locy_side= [0.0, 0.0, 0.0, 0.0, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, 0.0, 0.0, 0.0, 0.0, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64]
    locz_side= [1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45]

    locx_3d = [ 508.000, 285.800, 769.900, 0.000, -317.500, -879.900, -698.500, -934.900, -381.000, 0.000, 412.800, 1044.900,
              -1133.5, -1133.5, -1133.5, -1133.5, -566.75, -566.75, -566.75, -566.75, 566.75, 566.75, 566.75, 566.75, 1133.5, 1133.5, 1133.5, 1133.5, 566.75, 566.75, 566.75, 566.75, -566.75, -566.75, -566.75, -566.75]
    locy_3d = [0.000, 494.900, 444.500, 952.500, 549.900, 508.000, 0.000, -539.800, -659.900, -1143.000, -714.900, -603.300,
              0.0, 0.0, 0.0, 0.0, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, 0.0, 0.0, 0.0, 0.0, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64]
    locz_3d = [ -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950,
              1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45]

    for i in range(len(chg)):
        if i < 12:
            area.append(abs(chg[i])*30)
            area3.append(abs(chg[i])*30)
            colo.append(atime[i])
            colo3.append(atime[i])
        elif i < 36:
            if i>11 and i<16:
                dis_x.append(0)
            if i>15 and i<20:
                dis_x.append(60)
            if i>19 and i<24:
                dis_x.append(120)
            if i>23 and i<28:
                dis_x.append(180)
            if i>27 and i<32:
                dis_x.append(240)
            if i>31 and i< 36:
                dis_x.append(300)
            dis_y.append(locz_side[i-12])
            area2.append(abs(chg[i])*30)
            area3.append(abs(chg[i])*30)
            colo2.append(atime[i])
            colo3.append(atime[i])

    all_times = [t for t in colo if t is not None] + [t for t in colo2 if t is not None]
    if all_times:
        all_times_np = np.array(all_times)
        min_time = np.min(all_times_np[all_times_np > 10])
        max_time = np.max(all_times)
        vmin = min_time - 10
        vmax = max_time + 10
    else:
        vmin, vmax = None, None

    sc1 = ax1.scatter(locx_bot, locy_bot, s=area, c=colo, alpha=1, label="Bottom plane", vmin=vmin, vmax=vmax)
    sc2 = ax2.scatter(dis_x, dis_y, s=area2, c=colo2, alpha=1, label="Barrel plane", vmin=vmin, vmax=vmax)
    fig.colorbar(sc2, label="Peak time [ns]", ax=[ax1, ax2], orientation='vertical', shrink=0.8, pad=0.05)
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    ax2.set_xlabel("$\phi$ (deg.) with R = 1133 mm")
    ax2.set_ylabel("Z (mm)")
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')

    Drawing_uncolored_circle = plt.Circle( (0, 0 ), 1620, fill = False )
    ax1.set_aspect( 1 )
    ax1.add_artist( Drawing_uncolored_circle )
    ax1.set_xlim(-1650,1650)
    ax1.set_ylim(-1650,1650)

    linepos = 1503
    ax2.axhline(y=linepos, color='r', linestyle='-')
    ax2.axhline(y=-linepos, color='r', linestyle='-')

    sc3 = ax3d.scatter(locx_3d, locy_3d, locz_3d, s=area3, c=colo3, vmin=vmin, vmax=vmax)
    Xc,Yc,Zc = data_for_cylinder_along_z(0,0,1503,1625)
    ax3d.plot_surface(Xc, Yc, Zc, alpha=0.3)
    fig.colorbar(sc3, label="Peak time [ns]", ax=ax3d, fraction=0.036, pad=0.04)

    ax3d.set_title('LY in 3D')
    ax3d.set_xticks([-1600,-1400,-1200,-1000,-800,-600,-400,-200,0,200,400,600,800,1000,1200,1400,1600])
    ax3d.set_yticks([-1600,-1400,-1200,-1000,-800,-600,-400,-200,0,200,400,600,800,1000,1200,1400,1600])
    ax3d.set_zticks([-1600,-1400,-1200,-1000,-800,-600,-400,-200,0,200,400,600,800,1000,1200,1400,1600])
    ax3d.axes.set_xlim3d(left=-2000, right=2000)
    ax3d.axes.set_ylim3d(bottom=-2000, top=2000)
    ax3d.axes.set_zlim3d(bottom=-2000, top=2000)


def display_3d_grid(events_data, fig):
    """
    Plots a grid of 3D event displays.
    events_data: list of dictionaries, each containing {'chg': [], 'atime': [], 'event_id': int}
    fig: matplotlib figure object
    """
    n_events = len(events_data)
    if n_events == 0:
        return

    # Determine grid size (approx square)
    n_cols = int(np.ceil(np.sqrt(n_events)))
    n_rows = int(np.ceil(n_events / n_cols))

    # PMT Locations (copied from display_charge)
    locx_3d = [ 508.000, 285.800, 769.900, 0.000, -317.500, -879.900, -698.500, -934.900, -381.000, 0.000, 412.800, 1044.900,
              -1133.5, -1133.5, -1133.5, -1133.5, -566.75, -566.75, -566.75, -566.75, 566.75, 566.75, 566.75, 566.75, 1133.5, 1133.5, 1133.5, 1133.5, 566.75, 566.75, 566.75, 566.75, -566.75, -566.75, -566.75, -566.75]
    locy_3d = [0.000, 494.900, 444.500, 952.500, 549.900, 508.000, 0.000, -539.800, -659.900, -1143.000, -714.900, -603.300,
              0.0, 0.0, 0.0, 0.0, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, -981.64, 0.0, 0.0, 0.0, 0.0, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64, 981.64]
    locz_3d = [ -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950, -1035.950,
              1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45, 1254.35, 644.75, 35.15, -574.45]

    # Cylinder mesh
    Xc,Yc,Zc = data_for_cylinder_along_z(0,0,1503,1625)

    for i, event in enumerate(events_data):
        ax = fig.add_subplot(n_rows, n_cols, i + 1, projection='3d')
        
        chg = event['chg']
        atime = event['atime']
        event_id = event['event_id']

        area3 = []
        colo3 = []
        
        # Process charge and time (similar loop to display_charge but simplified for 3D only)
        for j in range(len(chg)):
             area3.append(abs(chg[j])*30)
             colo3.append(atime[j])

        # Determine vmin/vmax for colorbar consistency within this event
        if colo3:
            all_times_np = np.array(colo3)
            # Filter out very small times (zeros) if any, though atime usually > 0
            valid_times = all_times_np[all_times_np > 10]
            if valid_times.size > 0:
                min_time = np.min(valid_times)
                max_time = np.max(all_times_np)
                vmin = min_time - 10
                vmax = max_time + 10
            else:
                vmin, vmax = None, None
        else:
            vmin, vmax = None, None

        sc3 = ax.scatter(locx_3d, locy_3d, locz_3d, s=area3, c=colo3, vmin=vmin, vmax=vmax)
        ax.plot_surface(Xc, Yc, Zc, alpha=0.1) # Lighter alpha for grid view
        
        # Simplified axes for small plots
        ax.set_title(f'Event {event_id}', fontsize='small')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.axes.set_xlim3d(left=-2000, right=2000)
        ax.axes.set_ylim3d(bottom=-2000, top=2000)
        ax.axes.set_zlim3d(bottom=-2000, top=2000)



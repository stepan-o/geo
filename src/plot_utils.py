import contextily as ctx
import matplotlib.pyplot as plt


def plot_subset(df_full, plot_focus_id, focus_col, x_col, y_col1,
                format_axes=True, y_col2=None,
                p_x_label="x", p_y1_label="y1", p_y2_label="y2",
                get_address=True, return_subset=False):
    """
    Creates a subset from a provided DataFrame using parameters
    `plot_focus_id` to subset `focus_col` of the DataFrame `df_full`.

    Plots `x_col` as the x-axis, `y1_col` as a primary y-axis,
    and (optional) `y2_col` as a secondary y-axis.
    :param df_full: pandas DataFrame
        DataFrame with data to be plotted
    :param plot_focus_id: int or string
        index of interest, to create the subset
    :param focus_col: string
        column to use to create the subset from the DataFrame
    :param x_col: string
        column to sort the records by
    :param y_col1: string
        column to be plotted on 1st vertical axis
    :param format_axes: boolean
        whether to format y axes (default=True)
    :param y_col2: string
        column to be plotted on 2nd vertical axis
    :param p_x_label: string
        label to be used on the x axis
    :param p_y1_label: string
        label to be used for the primary y axis
    :param p_y2_label: string
        label to be used for the secondary y axis
    :param get_address: boolean
        whether to get the address and x y from the subset
        (default=True)
    :param return_subset: boolean
        whether to return the subset, address, and x y
        (default=False)
    :return: default: None, plots a chart
             optional:
                plot_subset: pandas DataFrame
                    DataFrame with the subset
                address: string
                    address obtained from the subset
                x, y: float
                    coordinates obtained from the subset
    """
    # generate subset by focus_col == focus_id
    subset_to_plot = df_full[df_full[focus_col] == plot_focus_id]
    if get_address:
        # get the address
        address = "{0} {1} {2}, {3}" \
            .format(subset_to_plot['street_number'].mode()[0],
                    subset_to_plot['street_name'].mode()[0],
                    subset_to_plot['street_designation'].mode()[0],
                    subset_to_plot['municipality'].mode()[0])
        x = subset_to_plot['x'].mode()[0]
        y = subset_to_plot['y'].mode()[0]
    else:
        address = ""
        x = ""
        y = ""
    # create figure and axes
    fig, axis = plt.subplots(1, figsize=(6, 6))
    # generate plot
    subset_to_plot.plot(x=x_col, y=y_col1, ax=axis)
    # format number display on y axis
    if format_axes:
        axis.get_yaxis() \
            .set_major_formatter(plt.FuncFormatter(lambda tick, loc: "{:,}".format(int(tick))))
    # set plot title
    axis.set_title("Rolling sum of Teranet transactions"
                   "\nfor pin: {0}".format(plot_focus_id) +
                   "\n{0:,} total records".format(len(subset_to_plot)) +
                   "\naddress: {0}".format(address) +
                   "\nx: {0}, y: {1}".format(x, y))
    axis.set_ylabel(p_y1_label)
    axis.set_xlabel(p_x_label)
    axis.grid(linestyle=':')

    if y_col2:
        # plot on secondary axis
        axis2 = axis.twinx()
        subset_to_plot.plot(x=x_col, y=y_col2,
                            ax=axis2, color='orange', alpha=0.5)
        # format number display on y axis
        if format_axes:
            axis2.get_yaxis() \
                .set_major_formatter(plt.FuncFormatter(lambda tick, loc: "{:,}".format(int(tick))))
        axis2.legend(loc='center left')
        axis2.set_ylabel(p_y2_label)

    plt.show()

    if return_subset:
        return subset_to_plot, address, x, y


def map_subset(gdf_to_plot, plot_focus_ids,
               color_col=None, plot_alpha=0.01,
               plot_title="", title_font_size=18,
               zoom_center=None, zoom_radius=None):
    """
    map a subset from a GeoDataFrame
    :param gdf_to_plot: geopandas GeoDataFrame
        GeoDataFrame with records to be mapped
    :param plot_focus_ids: pandas Series
        ids to be mapped, used to generate subset of GeoDataFrame
    :param color_col: string
        column to use to color points
    :param plot_alpha: float
        transparency of the points to be plotted
    :param plot_title:
        title to use for the map
    :param title_font_size:
        fontsize of the title
    :param zoom_center: tuple (int, int)
        central point of the zoom in CRS EPSG:3857 (Web Merkator projection, metres)
    :param zoom_radius: int or float
        radius of the zoom (x_min = zoom_center - radius, etc.)
        in meters (as per EPSG:3857)
    :return:
    """
    # plot results
    fig, axis = plt.subplots(1, figsize=(12, 12))
    gdf_to_plot.loc[plot_focus_ids].to_crs(epsg=3857) \
        .plot(column=color_col, legend=True,
              ax=axis, alpha=plot_alpha)
    if zoom_center:
        x_zoom, y_zoom = zoom_center
        axis.set_xlim(x_zoom - zoom_radius, x_zoom + zoom_radius)
        axis.set_ylim(y_zoom - zoom_radius, y_zoom + zoom_radius)

    # noinspection PyTypeChecker
    ctx.add_basemap(ax=axis,
                    url=ctx.sources.ST_TONER_HYBRID,
                    alpha=0.5)
    plt.title(plot_title, fontsize=title_font_size)
    plt.show()


def get_plot_title(counts, minrecords, id_lab):
    """
    helper function to generate plot title
    :param counts: pandas Series
        value counts from Teranet records (by pin, xy, da_id)
    :param minrecords: int
        minimum records per pin, xy, or da_id,
        used to filter Teranet counts
    :param id_lab: string
        label of the index (pin, xy, da_id, etc.)
    :return: title: string
        title of the plot
    """
    unique_ids = counts[counts > minrecords].index
    title = "{0}s with > {1:,} Teranet records" \
                .format(id_lab, minrecords) + \
            "\n{0:,} {1}s ({2:.5f}% of the total)" \
                .format(len(unique_ids),
                        id_lab,
                        len(unique_ids) / len(counts.index) * 100) + \
            "\n(coloured by count of records)"
    return title

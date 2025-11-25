import matplotlib.pyplot as plt

# copied from notebook just for sharing
def plot_xordered_data(
    data, x_name, y_name, label_name, loc=(0.8, 0.05), fit_line=False, fdr=False,
    xlabel=None, ylabel=None, title=None, axes=None, fig=None, legend=False,
    fit_params=True, hide_x=False, fontsize=12
):
    if fdr:
        p_col = "p_fdr"
    else:
        p_col = "pvals"

    if xlabel is None:
        xlabel = x_name
    if ylabel is None:
        ylabel = y_name
    if title is None:
        title = f"{ylabel} vs {xlabel}"

    if axes is None:
        fig, axes = plt.subplots(1)
    data.sort_values(by=x_name, inplace=True)
    for i, row in data.iterrows():
        c = row[x_name] / data[x_name].max()
        if p_col in data.columns and data.loc[i, p_col] >= 0.05:
            marker = "x"
        else:
            marker = "D"
        if legend:
            label = data.loc[i, label_name]
        else:
            label = None
        axes.scatter(
            data.loc[i, x_name],
            data.loc[i, y_name],
            marker=marker,
            color=viridis(c),
            label=label,
        )

    xlims = axes.get_xlim()
    ylims = axes.get_ylim()

    slope, intercept, r_value, p_value, std_err = stats.linregress(
            data[x_name], data[y_name])
    if fit_line:
        x = np.array([xlims[0], xlims[1]])
        y = slope * x + intercept
        axes.plot(x, y, c='black')
    
    if fit_params:
        text = "R2={:0.2f}\np={:0.2f}".format(r_value**2, p_value)
        text_y = ylims[0] + (ylims[1] - ylims[0]) * 0.9
        text_x = xlims[0] + (xlims[1] - xlims[0]) * 0.05
        axes.text(text_x, text_y, text, fontsize=fontsize)

    axes.set_xbound([xlims[0], xlims[1] * 1.1])
    if legend:
        axes.legend(loc=loc)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.set_title(title)
    if hide_x:
        axes.xaxis.set_major_formatter(plt.NullFormatter())
        axes.set_xlabel("")

    return fig, axes


# function call from my notebook
fig, axs = plt.subplots()
plot_xordered_data(
    data,
    "CP_dists",
    "coef",
    "struct",
    fit_line=True,
    title=f"MS\n struct ~ *{var_to_plot}* + {covariates_str}",
    axes=axs,
    fig=fig,
    legend=True,
    loc=(0.9, 0.0001),
    fdr=False,
)
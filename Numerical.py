import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from AdaptiveFramework import *
from NewtonFunctions import *
from UnregularizedThirdOrder import *
from matplotlib.lines import Line2D
import pickle


def plot_convergence_profile(result_dict, f_star, func_name, save_path=None):
    """
    绘制双图收敛行为分析图（含α_approx曲线）

    参数：
    - result_dict: 算法返回的结果字典
    - f_star: 目标函数的全局最小值
    - func_name: 函数名称（用于标题）
    - save_path: 图片保存路径（可选）
    """
    sigma_k = np.array(result_dict["sigma_history"][:-1])
    sigma_approx = np.array(result_dict["sigma_approx_history"])  
    f_values = np.array(result_dict["f_history"])
    iterations = np.arange(len(sigma_k))
    total_iter = result_dict["iterations"]
    converged = result_dict["converged"]

    f_diff = f_values - f_star
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=300, sharex=True)
    ax1.plot(
        iterations,
        sigma_approx.flatten(),
        color="darkorange",
        linestyle="--",
        linewidth=1.5,
        alpha=0.7,
        zorder=1,
        label=r"$\alpha_{k}^{LM}$",
    )

    marker_style = {
        "accepted": {"marker": "D", "s": 30},
        "rejected": {"marker": "o", "s": 25},
        "pre-rejected": {"marker": "x", "s": 25},
        "converged": {"marker": "v", "s": 40},
    }

    for k in iterations:
        is_converge_point = (k == total_iter - 1) and converged

        if is_converge_point:
            step_status = "converged"
        elif isinstance(result_dict["success_history"][k], str):
            step_status = "pre-rejected"
        elif result_dict["success_history"][k]:
            step_status = "accepted"
        else:
            step_status = "rejected"
        regularized = not np.isclose(sigma_k[k], 0, atol=1e-12)
        color = "royalblue" if regularized else "crimson"

        for ax, y_val in zip([ax1, ax2], [sigma_k[k], f_diff[k]]):
            ax.scatter(
                k,
                y_val,
                marker=marker_style[step_status]["marker"],
                s=marker_style[step_status]["s"],
                facecolor=color,
                edgecolor=color,
                linewidth=1.2,
                zorder=3 if is_converge_point else 2,
            )

    ax1.set_ylabel(r"$\sigma_k$", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.4)
    # ax1.set_yscale('log')  

    ax2.set_xlabel("Iteration (k)", fontsize=11)
    ax2.set_ylabel(r"$f(x_k) - f^*$", fontsize=11)
    ax2.set_yscale("log")
    ax2.grid(True, linestyle="--", alpha=0.4)

    legend_elements = [
        Line2D(
            [0],
            [0],
            color="darkorange",
            linestyle="--",
            lw=1.5,
            label=r"$\alpha_{k}^{LM}$",
            alpha=0.7,
        ),
        Line2D(
            [0],
            [0],
            marker="v",
            color="w",
            label="Converged Point",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            color="w",
            label="Accepted Step",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Rejected Step",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            marker="x",
            color="k",
            label="Pre-rejected Step",
            markersize=6,
            linewidth=1,
        ),
        Line2D([0], [0], color="crimson", lw=2, label=r"Unregularized"),
        Line2D([0], [0], color="royalblue", lw=2, label=r"Regularized"),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.05),
        ncol=3,
        fontsize=9,
        framealpha=0.9,
        handletextpad=0.3,
        columnspacing=0.8,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print(f"Saved to: {save_path}")
    else:
        plt.show()


def plot_multiple_convergence_profiles(
    result_dicts, f_star, func_name, param_combinations, save_path=None
):
    """
    绘制多个[l, eta]组合的双图收敛行为分析图。

    参数：
    - result_dicts: 含多个算法结果字典的列表，每个字典对应一个[l, eta]组合
    - f_star: 目标函数的全局最小值
    - func_name: 函数名称（用于标题）
    - param_combinations: [l, eta]组合列表，每个元素是一个二元组(l, eta)
    - save_path: 图片保存路径（可选）
    """
    n_params = len(param_combinations)

    fig, axes = plt.subplots(
        2 * n_params, 1, figsize=(15, 8 * n_params), dpi=300, sharex=True
    )

    if n_params == 1:
        axes = np.expand_dims(
            axes, axis=0
        )  # For single column, make axes 2D for consistency

    for idx, (result_dict, (l, eta)) in enumerate(
        zip(result_dicts, param_combinations)
    ):
        sigma_k = np.array(result_dict["sigma_history"][:-1])
        sigma_approx = np.array(result_dict["sigma_approx_history"]) 
        f_values = np.array(result_dict["f_history"])
        iterations = np.arange(len(sigma_k))
        total_iter = result_dict["iterations"]
        converged = result_dict["converged"]

        f_diff = f_values - f_star
        ax1 = axes[2 * idx]  # sigma_k subplot
        ax2 = axes[2 * idx + 1]  # f(x_k) - f* subplot

        ax1.plot(
            iterations,
            sigma_approx.flatten(),
            color="darkorange",
            linestyle="--",
            linewidth=1.5,
            alpha=0.7,
            zorder=1,
            label=r"$\alpha_{k}^{LM}$",
        )

        marker_style = {
            "accepted": {"marker": "D", "s": 30},
            "rejected": {"marker": "o", "s": 25},
            "pre-rejected": {"marker": "x", "s": 25},
            "converged": {"marker": "v", "s": 40},
        }

        for k in iterations:
            is_converge_point = (k == total_iter - 1) and converged

            if is_converge_point:
                step_status = "converged"
            elif isinstance(result_dict["success_history"][k], str):
                step_status = "pre-rejected"
            elif result_dict["success_history"][k]:
                step_status = "accepted"
            else:
                step_status = "rejected"

            # Jusify the regularization status
            regularized = not np.isclose(sigma_k[k], 0, atol=1e-12)
            color = "royalblue" if regularized else "crimson"

            for ax, y_val in zip([ax1, ax2], [sigma_k[k], f_diff[k]]):
                ax.scatter(
                    k,
                    y_val,
                    marker=marker_style[step_status]["marker"],
                    s=marker_style[step_status]["s"],
                    facecolor=color,
                    edgecolor=color,
                    linewidth=1.2,
                    zorder=3 if is_converge_point else 2,
                )

        ax1.set_ylabel(r"$\sigma_k$", fontsize=11)
        ax1.grid(True, linestyle="--", alpha=0.4)

        ax2.set_xlabel("Iteration (k)", fontsize=11)
        ax2.set_ylabel(r"$f(x_k) - f^*$", fontsize=11)
        ax2.set_yscale("log")
        ax2.grid(True, linestyle="--", alpha=0.4)
        ax1.set_title(f"l={l}, eta={eta}", fontsize=12)

    legend_elements = [
        Line2D(
            [0],
            [0],
            color="darkorange",
            linestyle="--",
            lw=1.5,
            label=r"$\alpha_{k}^{LM}$",
            alpha=0.7,
        ),
        Line2D(
            [0],
            [0],
            marker="v",
            color="w",
            label="Converged Point",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=8,
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            color="w",
            label="Accepted Step",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Rejected Step",
            markerfacecolor="black",
            markeredgecolor="k",
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            marker="x",
            color="k",
            label="Pre-rejected Step",
            markersize=6,
            linewidth=1,
        ),
        Line2D([0], [0], color="crimson", lw=2, label=r"Unregularized"),
        Line2D([0], [0], color="royalblue", lw=2, label=r"Regularized"),
    ]

    fig.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.99),
        ncol=3,
        fontsize=9,
        framealpha=0.9,
        handletextpad=0.3,
        columnspacing=0.8,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print(f"Saved to: {save_path}")
    else:
        plt.show()


def newton_fractal_dataset(func_name, max_iterations, tol, num_points, save_path=None):
    [fX, fx, dx, d2x, d3x] = init_func(func_name)
    [XMIN, XMAX, YMIN, YMAX, x_min] = init_params(func_name)

    x_points, y_points = num_points
    xlist = np.linspace(XMIN - 2.1, XMAX + 2.1, x_points)
    ylist = np.linspace(YMIN - 2.1, YMAX + 2.1, y_points)
    X, Y = np.meshgrid(xlist, ylist)

    fractal_data = {
        # "Newton": np.zeros_like(X),
        "Unregularized": np.zeros_like(X),
        "AURTON": np.zeros_like(X),
    }

    for i in range(x_points):
        for j in range(y_points):
            x0 = np.array([[xlist[i]], [ylist[j]]])

            # _, conv_newton = newton_run(fx, dx, d2x, d3x, x0, max_iterations, tol)
            _, conv_unreg = unregularized_third_newton_run(
                fx, dx, d2x, d3x, x0, max_iterations, tol
            )
            conv_ar3 = ar3_run(
                fx, dx, d2x, d3x, x0, max_iterations, tol, [0.1, 0.1, 0.01, 3]
            )["converged"]

            # fractal_data["Newton"][i, j] = conv_newton
            fractal_data["Unregularized"][i, j] = conv_unreg
            fractal_data["AURTON"][i, j] = conv_ar3

    # save the fractal data to a pickle file
    with open(save_path, "wb") as f:
        pickle.dump(fractal_data, f)
    print(f"Fractal data saved to {save_path}")
    return fractal_data


def newton_fractal_plot(func_name, num_points, dataset_path=None, save_path=None):
    [fX, fx, dx, d2x, d3x] = init_func(func_name)
    [XMIN, XMAX, YMIN, YMAX, x_min] = init_params(func_name)

    x_points, y_points = num_points
    xlist = np.linspace(XMIN - 2.1, XMAX + 2.1, x_points)
    ylist = np.linspace(YMIN - 2.1, YMAX + 2.1, y_points)
    X, Y = np.meshgrid(xlist, ylist)

    # Compute the contour data
    xlist_contour = np.linspace(XMIN - 2.2, XMAX + 2.2, 200)
    ylist_contour = np.linspace(YMIN - 2.2, YMAX + 2.2, 200)
    X_contour, Y_contour = np.meshgrid(xlist_contour, ylist_contour)
    Z = fX(X_contour, Y_contour)
    with open(dataset_path, "rb") as f:
        fractal_data = pickle.load(f)

    fig, axes = plt.subplots(1, 2, figsize=(18, 9))
    methods = ["Unregularized", "AURTON"]

    for ax, method in zip(axes, methods):
        cs = ax.contour(X_contour, Y_contour, np.log(Z), colors="orange")

        data = fractal_data[method]
        converged_mask = data == 1
        not_converged_mask = data == 0

        x_converged = X[converged_mask]
        y_converged = Y[converged_mask]
        x_not_converged = X[not_converged_mask]
        y_not_converged = Y[not_converged_mask]

        ax.scatter(x_converged, y_converged, c="green", s=15, marker="o")
        ax.scatter(x_not_converged, y_not_converged, c="red", s=15, marker="o")

        ax.set_title(method)
        ax.set_xlim(XMIN - 2.2, XMAX + 2.2)
        ax.set_ylim(YMIN - 2.2, YMAX + 2.2)
        ax.set_xlabel(r"$x_1$", fontsize=14)
        ax.set_ylabel(r"$x_2$", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.5)

    handles = [
        plt.Line2D([0], [0], color="green", lw=4, label="Converged"),
        plt.Line2D([0], [0], color="red", lw=4, label="Not Converged"),
        plt.Line2D([0], [0], color="orange", lw=2, label="Contour", linestyle="--"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        fontsize=12,
        bbox_to_anchor=(0.5, 1.06),
        ncol=3,
    )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
    else:
        plt.show()

    return fractal_data

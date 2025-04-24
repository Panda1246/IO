import base64
import io

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')


def create_bar_chart_base64(data_dict, title):

    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in sorted_items]
    values = [v for _, v in sorted_items]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color='skyblue')
    ax.set_title(title)
    ax.set_xlabel("Kategoria")
    ax.set_ylabel("Liczba")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_b64

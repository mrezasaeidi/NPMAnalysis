import pandas as pd


def cleaning():
    data_set = pd.read_csv("./edges_raw.csv")
    data_set = data_set.dropna(subset=['package_name', 'dependency'])
    not_found_packages = pd.read_csv('./not_found_packages.csv')

    data_set = data_set[~data_set['dependency'].isin(not_found_packages.packages)]
    data_set = data_set[data_set['package_name'] != data_set['dependency']]
    data_set.to_csv('./edges.csv', index=False)

    packages = set(data_set['package_name'])
    dependencies = set(data_set['dependency'])
    vertices = packages.union(dependencies)
    vertices = pd.DataFrame({'packages': list(vertices)})
    vertices.to_csv('./vertices.csv', index=False)


def get_top_libs():
    top_libs = pd.read_csv('./top_lib.csv')
    top_libs_names = []
    for p in top_libs["Repository_URL"]:
        package_name = p.split('/')[-1]
        top_libs_names.append(package_name)

    edges = pd.read_csv('./edges.csv')
    vertices = pd.read_csv('./vertices.csv')

    vertices = vertices[vertices.packages.isin(top_libs_names)]
    edges = edges[edges.package_name.isin(top_libs_names) & edges.dependency.isin(top_libs_names)]
    vertices.to_csv('./top_vertices.csv', index=False)
    edges.to_csv('./top_edges.csv', index=False)


def main():
    cleaning()
    get_top_libs()


if __name__ == '__main__':
    main()

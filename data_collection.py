import pandas as pd
import time
import requests

API_TOKENS = ["Define api tokens here"]

DELAY = 1 / len(API_TOKENS)


def get_packages_names(path):
    packages = pd.read_csv(path)
    packages_names = []
    for p in packages["Repository_URL"]:
        package_name = p.split('/')[-1]
        packages_names.append(package_name)

    return packages_names


def get_api_token(turn):
    tokens_count = len(API_TOKENS)
    index = turn % tokens_count
    return API_TOKENS[index]


def get_package_dependencies(package_name, turn):
    dependencies_df = pd.DataFrame(columns=["package_name", "dependency"])
    api_token = get_api_token(turn)
    url = f"https://libraries.io/api/NPM/{package_name}/latest/dependencies?api_key={api_token}"
    res = requests.get(url)

    if res.status_code < 200 or res.status_code > 299:
        print(f"error: {res.reason}")
        return None

    result = res.json()
    if result is None:
        return None

    dependencies = result["dependencies"]
    if dependencies is None:
        return None

    for i, d in enumerate(dependencies):
        name = d["name"]
        dependencies_df.loc[i] = {
            "package_name": package_name,
            "dependency": name
        }
    return dependencies_df


def get_edges(packages):
    packages = set(packages)
    explored = set()
    not_found_packages = []
    edges = pd.DataFrame(columns=["package_name", "dependency"])
    turn = 0
    while packages:
        print(f"Size(packages) = {len(packages)}, Size(explored) = {len(explored)}, Size(edges) = {len(edges)}")
        package = packages.pop()
        if package not in explored:
            explored.add(package)
            package_dependencies = get_package_dependencies(package, turn)
            turn += 1
            if package_dependencies is None:
                not_found_packages.append(package)
            else:
                for p in package_dependencies['dependency']:
                    if p not in explored:
                        packages.add(p)
                edges = edges._append(package_dependencies, ignore_index=True)
            time.sleep(DELAY)
    return edges, not_found_packages


def data_collection():
    packages = get_packages_names("./top_lib.csv")
    edges, not_found_packages = get_edges(packages)

    edges.to_csv("./edges_raw.csv", index=False)

    with open("./not_found_packages.csv", 'w') as file:
        file.write('packages\n')
        for name in not_found_packages:
            file.write(name + '\n')
    file.close()


def main():
    data_collection()


if __name__ == '__main__':
    main()

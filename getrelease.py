import requests
import json
from os.path import basename
from subprocess import run, getoutput

from test import data

def get_release():
    url = "https://api.github.com/repos/MetaCubeX/clash-verge/releases"
    return requests.get(url).json()[0]

def parse_arch(filename):
    if "amd64" in filename or "x86_64" in filename or "x64" in filename:
        return "x86_64"
    elif "arm64" in filename or "aarch64" in filename:
        return "arm64"

def parse_release(release):
    version = release['tag_name'].lstrip('v')
    assets = release['assets']
    result = []
    for asset in assets:
        if asset['name'].endswith('.deb'):
            result.append({"arch": parse_arch(asset['name']), "url": asset['browser_download_url']})
    return version, result

def dowlload_file(url, filename):
    r = requests.get(url, stream=True)
    if filename == None:
        filename = r.headers['Content-Disposition'].split('filename=')[1]
    if filename == None:
        raise Exception("filename is None")
    with open(filename, 'wb') as f:
        f.write(r.content)
    return filename

if __name__ == "__main__":
    release = get_release()
    version, tasks = parse_release(release)
    for task in tasks:
        downloaded = dowlload_file(task['url'], None)

        run(f"sudo alien -r -g {downloaded}", shell=True)

        dir = f"clash-verge-{version}"
        speffile = getoutput(f"ls {dir}/*.spec").split('\t')[0]

        run(f"sudo sed -i 's#\"/usr\"##' {speffile}", shell=True)
        run(f"sudo sed -i 's#\"/usr/share\"##' {speffile}", shell=True)
        run(f"sudo sed -i 's#\"/usr/bin\"##' {speffile}", shell=True)
        run(f"sudo sed -i 's#\"/usr/lib\"##' {speffile}", shell=True)

        # add dependency to the first line
        run(f"sudo sed -i '1iRequires: libappindicator-gtk3-devel' {speffile}", shell=True)


        run(f"cd {dir} && sudo rpmbuild --target={task['arch']} --buildroot $(pwd) -bb {basename(speffile)}", shell=True)



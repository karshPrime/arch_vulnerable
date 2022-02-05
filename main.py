#!/usr/bin/env python

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import subprocess


def get_distro():
    user_distro = str(subprocess.check_output("uname -n", shell=True), 'utf-8').strip().lower()
    return user_distro


def vul_pkgs():
    known_vulnerable = "https://security.archlinux.org/"
    link_soup = soup(uReq(known_vulnerable).read(), 'html.parser')
    package_list = [vulnerables := [], severity := []]

    counter = 1
    for package in link_soup.find("tbody").findAll("td"):
        if counter == 3:    # Package Name
            vulnerables.append(package.a.text)
        
        elif counter == 6:  # severity
            severity.append(package.span.text)
        
        elif counter == 9:  # final column
            counter = 0

        counter += 1

    return(package_list)


def installed_list(distro):
    # Arch based
    if distro in ['arch', 'endeavour', 'manjaro']:
        all_packages = "pacman -Qq"
    
    # Debian based
    elif distro in ['debian', 'ubuntu', 'kali', 'pop_os']:
        all_packages = 'dpkg --get-selections | grep -v deinstall'

    # RHEL based
    elif distro in ['fedora', 'centos']:
        all_packages = "dnf list | awk \'{split($0,a,\".\"); print a[1]}'"

    else:
        print("distro not recognized")
        return -1
    
    return str(subprocess.check_output(all_packages, shell=True), 'utf-8').split("\n")


def list_compare(installed, vulnerables):
    indexes = []
    for pkg in installed:
        for i in range(len(vulnerables)-1):
            if vulnerables[i] == pkg:
                indexes.append(i)

    return indexes


def list_output(vulnerables, indexes):
    for i in indexes:
        space = '\t\t\t'
        if len(vulnerables[0][i]) > 5:
            space = '\t\t'
        elif len(vulnerables[0][i]) > 13:
            space = '\t'

        print(f"> \033[33m{vulnerables[0][i]}{space}\033[0m\033[;37m[{vulnerables[1][i]}]\033[0m")


def main():
    user_distro = get_distro()
    installed_pkgs = installed_list(user_distro)
    vulnerables = vul_pkgs()
    indexes = list_compare(installed_pkgs, vulnerables[0])
    list_output(vulnerables, indexes)

main()

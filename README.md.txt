# sec-sample-3
A deployment version of this app can be found at https://dash.thesystech.com/z-sec-sample-3.

![screenshot](screenshot.png "screenshot")

## requirements

- python
- conda

## installation

```shell
conda install --no-update-deps --file conda-requirements.txt --yes
```

## local usage

Please note that the included `.condarc` is used on Dash Enterprise to refer to remote conda packages for both internal and Plotly-maintained commercial packages. The channels referenced may be incorrect when not used within the airgapped environment.

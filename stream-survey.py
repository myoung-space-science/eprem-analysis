import argparse
import typing

import matplotlib.pyplot as plt

from eprempy import eprem
from eprempy import quantity
from eprempy.paths import fullpath
from support import plots


UNITS = {
    'time': 'hour',
    'energy': 'MeV',
    'flux': '1 / (cm^2 s sr MeV/nuc)',
    'fluence': '1 / (cm^2 sr MeV/nuc)',
    'integral flux': '1 / (cm^2 s sr)',
}


def main(
    num: int=None,
    indir: str=None,
    config: str=None,
    outdir: str=None,
    verbose: bool=False,
    **user
) -> None:
    """Create survey plots for one or more stream observers."""
    source = indir or '.'
    dataset = eprem.dataset(source=source, config=config)
    streams = get_streams(dataset, num)
    plotdir = fullpath(outdir or source)
    plotdir.mkdir(parents=True, exist_ok=True)
    for stream in streams:
        plot_stream(stream, **user)
        plotpath = plotdir / stream.source.with_suffix('.png').name
        if verbose:
            print(f"Saved {plotpath}")
        plt.savefig(plotpath)
        if user.get('show'):
            plt.show()
        plt.close()


def get_streams(dataset: eprem.Dataset, num: typing.Optional[int]=None):
    """Get all relevant stream observers."""
    streams = dataset.streams
    if isinstance(num, int):
        return [streams[num]]
    return list(streams.values())


def plot_stream(stream: eprem.Observer, **user):
    """Create a survey plot for this stream."""
    fig, axs = plt.subplots(
        nrows=1,
        ncols=3,
        squeeze=True,
        figsize=(20, 6),
        layout='constrained',
    )
    location = get_location(user)
    species = get_species(user)
    units = {q: user.get(f'{q}', u) for q, u in UNITS.items()}
    ylim = user.get('flux_ylim')
    plots.flux(axs[0], stream, location, species, units, ylim)
    ylim = user.get('fluence_ylim')
    plots.fluence(axs[1], stream, location, species, units, ylim)
    ylim = user.get('intflux_ylim')
    plots.intflux(axs[2], stream, location, species, units, ylim)
    fig.suptitle(make_suptitle(stream, location, species), fontsize=20)


def get_location(user: dict):
    """Get the shell or radius at which to plot."""
    shell = user.get('shell')
    if shell is not None: # allow value to be 0
        return shell
    if radius := user.get('radius'):
        return quantity.measure(float(radius[0]), radius[1]).withunit('au')
    return 0


def get_species(user: dict):
    """Get the ion species to plot."""
    species = user.get('species')
    if species is not None: # allow value to be 0
        return species
    return 0


def make_suptitle(
    stream: eprem.Stream,
    location: typing.Union[int, quantity.Measurement],
    species: typing.Union[int, str],
) -> str:
    """Create the top-level plot title."""
    if isinstance(location, quantity.Measurement):
        strloc = f"radius = {float(location)} {location.unit}"
    elif isinstance(location, int):
        strloc = f"shell = {location}"
    else:
        raise TypeError(location)
    if isinstance(species, int):
        strspe = f"species = {stream.species.data[species]}"
    elif isinstance(species, str):
        strspe = f"species = {species}"
    else:
        raise TypeError(species)
    return f"{strloc} | {strspe}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-n', '--stream',
        dest='num',
        help="which stream to show",
        type=int,
    )
    parser.add_argument(
        '-c', '--config',
        help="name of simulation configuration file (default: eprem.cfg)",
    )
    parser.add_argument(
        '-i', '--input',
        dest='indir',
        help="directory containing simulation data (default: current)",
    )
    parser.add_argument(
        '-o', '--output',
        dest='outdir',
        help="output directory (default: input directory)",
    )
    location = parser.add_mutually_exclusive_group()
    location.add_argument(
        '--shell',
        help="shell at which to plot flux (default: 0)",
        type=int,
    )
    location.add_argument(
        '--radius',
        help="radius at which to plot flux (default: inner boundary)",
        nargs=2,
        metavar=('RADIUS', 'UNIT'),
    )
    parser.add_argument(
        '--species',
        help=(
            "ion species to plot"
            "; may be symbol or index (default: 0)"
        ),
    )
    parser.add_argument(
        '--time-unit',
        help="metric unit in which to display times",
    )
    parser.add_argument(
        '--energy-unit',
        help="metric unit in which to display energies",
    )
    parser.add_argument(
        '--flux-ylim',
        help="y-axis limits for flux",
        nargs=2,
        type=float,
        metavar=('LO', 'HI'),
    )
    parser.add_argument(
        '--fluence-ylim',
        help="y-axis limits for fluence",
        nargs=2,
        type=float,
        metavar=('LO', 'HI'),
    )
    parser.add_argument(
        '--intflux-ylim',
        help="y-axis limits for integral flux",
        nargs=2,
        type=float,
        metavar=('LO', 'HI'),
    )
    parser.add_argument(
        '-v', '--verbose',
        help="print runtime messages",
        action='store_true',
    )
    parser.add_argument(
        '--show',
        help="display the plot on the screen",
        action='store_true',
    )
    args = parser.parse_args()
    main(**vars(args))

import os
# import StringIO

import click

from gitstats import log
from gitstats.utils import (
    discover_repositories, generate_git_log, make_svg_report, process_log,
    sort_by_year)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--year', type=str, help='Specify a year or \'all\'')
@click.option('--email', help='My email address', multiple=True, required=True)
def analyze(path, year, email):
    repositories = discover_repositories(os.path.expanduser(path))

    gitlogs = []
    for repo in repositories:
        try:
            gitlogs += generate_git_log(repo)
        except RuntimeError:
            log.warn('Not able to generate logs for {}', path)

    gitlog_by_year = sort_by_year(gitlogs)

    max_commits = []
    for y in gitlog_by_year:
        data = process_log(gitlog_by_year[y], y, email)
        max_commits.append(data['max_commits'])

    if not year:
        try:
            year = y
        except NameError:
            # When running `generate_git_log()` for an empty repository,
            # `gitlog_by_year` becomes an empty list and `y` won't have a
            # chance to be assigned. We will refactor this function entirely so
            # we will stick with the following temporary workaround.
            log.info('{} appears to be an empty repository', path)
            return
    else:
        year = int(year)
    global_max = max(max_commits)
    processed_logs = process_log(gitlog_by_year[year], year, email)

    log.info('Generating report for year {}'.format(year))
    make_svg_report(processed_logs, global_max)


if __name__ == '__main__':
    cli()

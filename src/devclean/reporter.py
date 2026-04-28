from rich.console import Console
from rich.panel import Panel
from devclean.cleaner import CleanResult

console = Console()

def print_header(root: str) -> None:
    console.print(Panel(f"[bold cyan]devclean[/]  scanning [bold]{root}[/]"))

def format_size(size_mb: float) -> str:
    """Format size into MB or GB."""
    if size_mb > 1024:
        return f"{size_mb/1024:.1f} GB"
    return f"{size_mb:.1f} MB"

def print_result(result: CleanResult) -> None:
    """
    Prints one line per result.

    Format:
      found    node_modules    my-react-app    234.5 MB   (dry run)
      deleted  node_modules    my-react-app    234.5 MB
      skipped  __pycache__     py-pie            0.0 MB   (already gone)
    """

    if result.deleted:
        status = "deleted"
    elif not result.path.exists() and result.size_mb == 0.0:
        status = "skipped"
    else:
        status = "found"
    
    parent_name = result.path.parent.name 
    size_str = format_size(result.size_mb)
    
    line = f"{status:<8} {result.name:<15} {parent_name:<20} {size_str:>10}"

    if not result.deleted and result.size_mb > 0:
        line += "   (dry run)"
    elif status == "skipped":
        line += "   (already gone)"

    if status == "deleted":
        console.print(f"  [green]✓[/]  {line}")
    elif status == "found":
        console.print(f"  [yellow]✓[/]  {line}")
    else:
        console.print(f"  [red]✗[/]  {line}")

def print_summary(results: list[CleanResult], dry_run: bool) -> None:
    total_mb = sum(r.size_mb for r in results)
    count = len(results)
    size_str = format_size(total_mb)
 
    if dry_run:
        summary = f"[bold]{count}[/] folders found  ·  [bold]{size_str}[/] reclaimable"
    else:
        deleted = sum(1 for r in results if r.deleted)
        skipped = count - deleted
        summary = f"[bold]{deleted}[/] folders deleted  ·  [bold]{size_str}[/] freed"
        if skipped:
            summary += f"  [dim]({skipped} skipped)[/]"
 
    console.print()
    console.print(Panel(summary))
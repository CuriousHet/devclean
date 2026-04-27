from devclean.cleaner import CleanResult

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

    print(line)

def print_summary(results: list[CleanResult], dry_run: bool) -> None:
    total_mb = sum(r.size_mb for r in results)
    count = len(results)
    size_str = format_size(total_mb)

    print()
    if dry_run:
        print(f"  {count} folders found · {size_str} reclaimable")
    else:
        deleted = sum(1 for r in results if r.deleted)
        skipped = count - deleted
        print(f"  {deleted} folders deleted · {size_str} freed", end="")
        if skipped:
            print(f"  ({skipped} skipped)", end="")
        print()
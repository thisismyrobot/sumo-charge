import timeit


# Usually about 0.95 per snapshot
print 'get_frame.snapshot(): {}'.format(
    timeit.timeit(stmt='get_frame.snapshot()', setup='import get_frame', number=5) / 5
)

# Usually about 0.75 per snapshot
print 'get_frame.snapshot_ftp(): {}'.format(
    timeit.timeit(stmt='get_frame.snapshot_ftp()', setup='import get_frame', number=5) / 5
)

# Usually about 0.55 per snapshot
print 'get_frame.snapshot_socket(): {}'.format(
    timeit.timeit(stmt='get_frame.snapshot_socket()', setup='import get_frame', number=5) / 5
)

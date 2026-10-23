def merge_intervals(segments):
    if not segments:
        return []
    segments.sort(key=lambda item: item[0])
    combined_list = [segments[0]]
    for item in segments[1:]:
        last_seg = combined_list[-1]
        if item[0] <= last_seg[1]:
            last_seg[1] = max(last_seg[1], item[1])
        else:
            combined_list.append(item)
    return combined_list

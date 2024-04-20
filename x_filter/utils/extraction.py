from typing import List

from x_filter.data.models.filter import ExtractedFilters, Filter

def extract_filters(stage2: ExtractedFilters, filter: Filter) -> ExtractedFilters:
    """
    Extract filters from the filter_prompt into the filter object
    """
    extracted_filters = Filter(
        id=filter.id,
        user_id=filter.user_id,
        target=filter.target,
        primary_prompt=filter.primary_prompt,
        report_guide=filter.report_guide,
        filter_prompt=stage2.filter_prompt,
        filter_period=stage2.filter_period if stage2.filter_period is not None else ExtractedFilters.filter_period.default,
        usernames=stage2.usernames if stage2.usernames is not None else ExtractedFilters.usernames.default,
        only_search_specified_usernames=stage2.only_search_specified_usernames if stage2.only_search_specified_usernames is not None else ExtractedFilters.only_search_specified_usernames.default,
        only_search_followers=stage2.only_search_followers if stage2.only_search_followers is not None else ExtractedFilters.only_search_followers.default,
        keyword_groups=stage2.keyword_groups if stage2.keyword_groups is not None else ExtractedFilters.keyword_groups.default,
        return_cap=stage2.return_cap if stage2.return_cap is not None else ExtractedFilters.return_cap.default,
    )
    return extracted_filters

def combine_keyword_groups(keyword_groups_1: List[List[str]], keyword_groups_2: List[List[str]]) -> List[List[str]]:
    """
    Combine two keyword groups into one, removing any duplicates where order does not matter.
    """
    combined = keyword_groups_1 + keyword_groups_2
    unique_combined = []
    for group in combined:
        if sorted(group) not in [sorted(g) for g in unique_combined]:
            unique_combined.append(group)
    return unique_combined

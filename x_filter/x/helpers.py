
def build_combined_query(keyword_groups, exclude_replies: bool = True):
    """
    Constructs a Twitter search query string from a list of keyword groups. Each group is combined using 'AND',
    and each resulting group string is then combined with 'OR' between them. Ensures correct formatting to avoid ambiguity.
    
    Args:
        keyword_groups (list of list of str): A list where each element is a list of keywords to be ANDed together.
    
    Returns:
        str: A combined query string integrating both 'AND' and 'OR' conditions, formatted for Twitter API requirements.
    """
    combined_queries = []
    
    for keywords in keyword_groups:
        # Enclose keywords in quotes only if they contain spaces
        quoted_keywords = [f'"{keyword}"' if ' ' in keyword else keyword for keyword in keywords]
        # Join keywords in each group with ' AND ' ensuring correct spacing
        and_query = ' '.join(quoted_keywords)
        # Enclose each and_query in parentheses to ensure proper grouping
        combined_queries.append(f"({and_query})")
    
    # Join all group queries with ' OR ', ensuring correct spacing
    final_query = ' OR '.join(combined_queries)
    
    if exclude_replies:
        final_query += " -is:reply"
    
    return final_query
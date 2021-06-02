from django.shortcuts import render
from datetime import datetime, timezone
from django.core.paginator import EmptyPage, Paginator
from arxiv import Search, SortCriterion
from pymed import PubMed
# from gtts import gTTS

# Create your views here.


def article_search_view(request):
    return render(request, 'article/article_search_template.html')


def get_articles_view(request):
    context = {}
    query = context['query'] = request.GET["query"]
    oldnessindays = context['oldnessindays'] = int(
        request.GET["oldnessindays"])
    publication = context['publication'] = request.GET["publication"]
    max_results = context['maxnoofpapers'] = int(request.GET["maxnoofpapers"])
    search_results = []

    if(publication == 'Arxiv'):

        words_in_query = query.split()
        if len(words_in_query) > 1:
            query = " AND ".join(words_in_query)

        query_results = Search(
            query=query, max_results=max_results, sort_by=SortCriterion.SubmittedDate).get()

        for query_result in query_results:
            authors = [author.name for author in query_result.authors]
            tospeak = "title "+(query_result.title or "") + \
                " abstract "+(query_result.summary or "")
            tospeak = tospeak.replace("\n", " ")
            query_result.summary = (query_result.summary or "")
            if len(query_result.summary.split()) > 100:
                summary_short = " ".join(query_result.summary.split()[:99])
                summary_full = " ".join(query_result.summary.split()[99:])
            else:
                summary_short = query_result.summary
                summary_full = ""
            article = {"title": query_result.title, "abstract": summary_short, "abstract_full": summary_full,
                       "authors": authors, "published": query_result.updated, "tospeak": tospeak}
            search_results.append(article)

    elif(publication == 'PubMed'):

        pubmed = PubMed(tool="paperwhisperer",
                        email="rishabkoul2001@gmail.com")

        query_results = pubmed.query(query, max_results=max_results)
        authors = []
        for query_result in query_results:
            for author in query_result.authors:
                if(author['firstname'] != None and author['lastname'] != None):
                    authors.append(author['firstname']+' '+author['lastname'])
                elif(author['firstname'] == None and author['lastname'] != None):
                    authors.append(author['lastname'])
                elif(author['firstname'] != None and author['lastname'] == None):
                    authors.append(author['firstname'])
                else:
                    authors.append('unknown')

            midnight_time = datetime.min.time()
            publication_date = datetime.combine(
                query_result.publication_date, midnight_time).astimezone()

            tospeak = "title "+(query_result.title or "") + \
                " abstract "+(query_result.abstract or "")
            tospeak = tospeak.replace("\n", " ")

            query_result.abstract = (query_result.abstract or "")
            if len(query_result.abstract.split()) > 100:
                summary_short = " ".join(query_result.abstract.split()[:99])
                summary_full = " ".join(query_result.abstract.split()[99:])
            else:
                summary_short = query_result.abstract
                summary_full = ""

            article = {"title": query_result.title, "abstract": summary_short, "abstract_full": summary_full,
                       "authors": authors, "published": publication_date, "tospeak": tospeak}
            search_results.append(article)

    else:
        queryarxiv = query
        words_in_query = query.split()
        if len(words_in_query) > 1:
            queryarxiv = " AND ".join(words_in_query)

        query_results = Search(
            query=queryarxiv, max_results=max_results, sort_by=SortCriterion.SubmittedDate).get()

        for query_result in query_results:
            authors = [author.name for author in query_result.authors]
            tospeak = "title "+(query_result.title or "") + \
                " abstract "+(query_result.summary or "")
            tospeak = tospeak.replace("\n", " ")
            query_result.summary = (query_result.summary or "")
            if len(query_result.summary.split()) > 100:
                summary_short = " ".join(query_result.summary.split()[:99])
                summary_full = " ".join(query_result.summary.split()[99:])
            else:
                summary_short = query_result.summary
                summary_full = ""

            article = {"title": query_result.title, "abstract": summary_short, "abstract_full": summary_full,
                       "authors": authors, "published": query_result.updated, "tospeak": tospeak}
            search_results.append(article)

        pubmed = PubMed(tool="paperwhisperer",
                        email="rishabkoul2001@gmail.com")

        query_results = pubmed.query(query, max_results=max_results)
        authors = []
        for query_result in query_results:
            for author in query_result.authors:
                if(author['firstname'] != None and author['lastname'] != None):
                    authors.append(author['firstname']+' '+author['lastname'])
                elif(author['firstname'] == None and author['lastname'] != None):
                    authors.append(author['lastname'])
                elif(author['firstname'] != None and author['lastname'] == None):
                    authors.append(author['firstname'])
                else:
                    authors.append('unknown')

            midnight_time = datetime.min.time()
            publication_date = datetime.combine(
                query_result.publication_date, midnight_time).astimezone()

            tospeak = "title "+(query_result.title or "") + \
                " abstract "+(query_result.abstract or "")
            tospeak = tospeak.replace("\n", " ")
            query_result.abstract = (query_result.abstract or "")
            if len(query_result.abstract.split()) > 100:
                summary_short = " ".join(query_result.abstract.split()[:99])
                summary_full = " ".join(query_result.abstract.split()[99:])
            else:
                summary_short = query_result.abstract
                summary_full = ""

            article = {"title": query_result.title, "abstract": summary_short, "abstract_full": summary_full,
                       "authors": authors, "published": publication_date, "tospeak": tospeak}
            search_results.append(article)

    articles_not_older_than_days = []
    for article in search_results:
        days_from_publication = (datetime.now(
            timezone.utc).astimezone() - article['published']).days
        if oldnessindays >= days_from_publication:
            articles_not_older_than_days.append(article)

    p = Paginator(articles_not_older_than_days, 1)

    page_num = request.GET.get('page', 1)

    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    # audio = gTTS(text=page.object_list[0]['tospeak'], lang='en', slow=False)
    # audio.save("static/audio.mp3")

    context['search_results'] = page

    return render(request, 'article/article_alldisplay_template.html', context)

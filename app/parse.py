from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text for tag in quote.select("a.tag")],
    )


def get_single_quote_page(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select_one(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> [Quote]:
    response = requests.get(BASE_URL).content
    soup = BeautifulSoup(response, "html.parser")
    quotes = soup.select(".quote")
    all_quotes = [parse_single_quote(quote) for quote in quotes]

    if soup.select_one(".next"):
        while soup.select_one(".next"):
            next_page = soup.select_one(".next").select_one("a").get("href")
            response = requests.get(BASE_URL + next_page).content
            soup = BeautifulSoup(response, "html.parser")
            quotes = soup.select(".quote")

            for quote in quotes:
                all_quotes.append(parse_single_quote(quote))
    return all_quotes


def write_to_quotes_csv(quotes: list[Quote], path: str) -> None:
    with open(f"{path}", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_to_quotes_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")

import csv
import os
import requests

from django.core.management.base import BaseCommand
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from bs4 import BeautifulSoup

from src.artworks.models import Artist, Artwork


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Artist data parsing
        # artist_data_file_path = os.path.join(settings.STATIC_ROOT, 'artist_data.csv')

        # with open(artist_data_file_path, encoding="utf8") as csv_file:
        #     csv_reader = csv.DictReader(csv_file)
        #     line_count = 0
        #     for row in csv_reader:
        #         if line_count == 0:
        #             print(f'Column names are {", ".join(row)}')
        #             line_count += 1
        #         print(f'\t Artist {row["name"]}, Gender: {row["gender"]}, Date: {row["dates"]}.')

        #         Artist.objects.get_or_create(name=row['name'], defaults={
        #             'gender': row['gender'],
        #             'dates': row['dates']
        #         })
        #         line_count += 1

        #     print(f'Processed {line_count} lines.')

        # Artwork data parsing

        artwork_data_file_path = os.path.join(settings.STATIC_ROOT, 'artwork_data.csv')

        with open(artwork_data_file_path, encoding="utf8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                line_count += 1
                if line_count < 800:
                    continue

                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    continue

                if not 'url' in row or not row['url']:
                    continue

                r = requests.get(row['url'], verify=False)
                soup = BeautifulSoup(r.content)
                container = soup.find('div', attrs={'class': 'image-container'})

                if not container:
                    continue

                img = container.find('img')

                if not img or not img.get('data-original'):                    
                    continue

                response = requests.get(img['data-original'].replace('_7', '_10'), verify=False)

                if response.status_code != 200:
                    continue

                artwork_image_path = os.path.join('artwork_images', f"{row['accession_number']}.jpg")
                with open(os.path.join(settings.MEDIA_ROOT, artwork_image_path), "wb") as new_img:
                    new_img.write(response.content)

                artist, _ = Artist.objects.get_or_create(name=row['artist'], defaults={})

                # artwork, created = Artwork.objects.get_or_create(
                #     title=row['title'],
                #     description=f"{row['medium']} {row['creditLine']}", 
                #     defaults={
                #         'dimensions': row['dimensions'],
                #         'date': row['dateText'],
                #         'image': artwork_image_path
                #     }
                # )
                data = {
                    'title': row['title'],
                    'description': f"{row['medium']} {row['creditLine']}",
                    'dimensions': row['dimensions'][:50],
                    'date': row['dateText'],
                    'image': artwork_image_path
                }

                artwork = Artwork.objects.create(**data)

                print(f"Artwork {row['title']} was created[{True}].")

                artist.artworks.add(artwork)


            print(f'Processed {line_count} lines.')
            

        

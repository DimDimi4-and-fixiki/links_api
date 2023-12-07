async def test_visited_links(test_app, patch_time):
    patch_time(time=10)
    resp_post = await test_app.post(
        '/api/v1/visited_links/',
        json={
            'links': [
                'https://example.com/',
            ]
        },
    )

    assert resp_post.json() == {'status': 'ok'}

    patch_time(time=20)
    resp_post = await test_app.post('/api/v1/visited_links/', json={'links': ['https://my-site.com/', 'http://some-links.com/']})

    assert resp_post.json() == {'status': 'ok'}

    resp_to_10 = await test_app.get('/api/v1/visited_domains/?from_time=9&to_time=10')
    resp_to_20 = await test_app.get('/api/v1/visited_domains/?from_time=0&to_time=20')

    assert resp_to_10.json() == {'domains': ['example.com'], 'status': 'ok'}
    assert resp_to_20.json() == {'domains': ['example.com', 'my-site.com', 'some-links.com'], 'status': 'ok'}


async def test_visited_links_error(test_app):
    resp_post = await test_app.post(
        '/api/v1/visited_links/',
        json={
            'links': [
                'invalid_link',
            ]
        },
    )

    assert resp_post.status_code == 400
    assert 'Validation error' in resp_post.json().get('status')

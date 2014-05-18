from django.core.urlresolvers import reverse
from sentry.models import Project
from sentry.testutils import APITestCase


class TeamProjectIndexTest(APITestCase):
    def test_simple(self):
        self.login_as(user=self.user)
        team = self.create_team(slug='baz')
        project_1 = self.create_project(team=team, slug='fiz')
        project_2 = self.create_project(team=team, slug='buzz')

        url = reverse('sentry-api-0-team-project-index', kwargs={
            'team_id': team.id,
        })
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 2
        assert sorted(map(lambda x: x['id'], response.data)) == sorted([
            str(project_1.id),
            str(project_2.id),
        ])


class TeamProjectCreateTest(APITestCase):
    def test_simple(self):
        self.login_as(user=self.user)
        team = self.create_team(slug='baz')
        url = reverse('sentry-api-0-team-project-index', kwargs={
            'team_id': team.id,
        })
        resp = self.client.post(url, data={
            'name': 'hello world',
            'slug': 'foobar',
        })
        assert resp.status_code == 201, resp.content
        project = Project.objects.get(id=resp.data['id'])
        assert project.name == 'hello world'
        assert project.slug == 'foobar'
        assert project.owner == self.user
        assert project.team == team

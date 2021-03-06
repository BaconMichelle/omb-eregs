import pytest
import reversion
from model_mommy import mommy
from reversion.models import Version

from reqs.models import Agency, Policy, Requirement, Topic


def test_reqs_in_topics(admin_client):
    """We can see a listing of requirements within the topic edit screen"""
    req1, req2, req3 = mommy.make(Requirement, _quantity=3)
    key1 = mommy.make(Topic, name='key1')
    key2 = mommy.make(Topic, name='key2')
    key3 = mommy.make(Topic, name='key3')
    key4 = mommy.make(Topic, name='key4')
    req1.topics.add(key1, key2)
    req2.topics.add(key2, key3)
    req3.topics.add(key3, key4)

    def admin_text(pk):
        resp = admin_client.get('/admin/reqs/topic/{0}/change/'.format(pk))
        return resp.content.decode('utf-8')

    result = admin_text(key1.pk)
    assert req1.req_id in result
    assert req2.req_id not in result
    assert req3.req_id not in result

    result = admin_text(key2.pk)
    assert req1.req_id in result
    assert req2.req_id in result
    assert req3.req_id not in result

    result = admin_text(key3.pk)
    assert req1.req_id not in result
    assert req2.req_id in result
    assert req3.req_id in result

    result = admin_text(key4.pk)
    assert req1.req_id not in result
    assert req2.req_id not in result
    assert req3.req_id in result


def test_reqs_in_policy(admin_client):
    """We can see a listing of requirements within the policy edit screen"""
    policy1, policy2, policy3 = mommy.make(Policy, _quantity=3)
    req1 = mommy.make(Requirement, policy=policy1)
    req2 = mommy.make(Requirement, policy=policy1)
    req3 = mommy.make(Requirement, policy=policy2)

    def admin_text(pk):
        resp = admin_client.get('/admin/reqs/policy/{0}/change/'.format(pk))
        return resp.content.decode('utf-8')

    result = admin_text(policy1.pk)
    assert req1.req_id in result
    assert req2.req_id in result
    assert req3.req_id not in result

    result = admin_text(policy2.pk)
    assert req1.req_id not in result
    assert req2.req_id not in result
    assert req3.req_id in result

    result = admin_text(policy3.pk)
    assert req1.req_id not in result
    assert req2.req_id not in result
    assert req3.req_id not in result


def test_topics_displayed(admin_client):
    """Existing topics should be in the markup of a requirement edit page"""
    topics = mommy.make(Topic, _quantity=4)
    req = mommy.make(Requirement)
    req.topics.set(topics)

    resp = admin_client.get('/admin/reqs/requirement/{0}/change/'.format(
        req.pk))
    markup = resp.content.decode('utf-8')
    for topic in topics:
        assert topic.name in markup


def req_query_str():
    """Create a requirement and generate the query string associated with
    it"""
    req = mommy.prepare(Requirement, policy=mommy.make(Policy))
    fields = {f.name: getattr(req, f.name) for f in req._meta.fields}
    fields['policy'] = req.policy_id
    return '&'.join('{0}={1}'.format(k, v) for k, v in fields.items())


@pytest.mark.django_db
def test_reversion():
    with reversion.create_revision():
        key = mommy.make(Topic, name="key1")

    key_from_db = Topic.objects.get(pk=key.pk)
    assert key.name == key_from_db.name

    with reversion.create_revision():
        key_from_db.name = "new name"
        key_from_db.save()

    key.refresh_from_db()
    assert key.name == "new name"
    assert key_from_db.name == "new name"

    versions = Version.objects.get_for_model(Topic)
    assert len(versions) == 2
    assert versions[1].field_dict["name"] == "key1"
    assert versions[0].field_dict["name"] == "new name"

    versions[1].revision.revert()

    key.refresh_from_db()
    assert key.name == "key1"


@pytest.mark.django_db
def test_agency_form(admin_client):
    agency = mommy.make(Agency)
    resp = admin_client.get('/admin/reqs/agency/{0}/change/'.format(
        agency.pk))

    markup = resp.content.decode('utf-8')
    assert 'Editable fields' in markup
    assert 'Imported fields' in markup
    assert 'name="public"' in markup
    assert 'name="name"' not in markup
    assert 'name="abbr"' not in markup


def test_agency_cannot_be_added(admin_client):
    resp = admin_client.get('/admin/reqs/agency/add/')
    assert resp.status_code == 403

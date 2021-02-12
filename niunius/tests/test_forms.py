from niunius import forms


def test_article_form_with_no_data():
    form = forms.ArticleForm(data={})
    assert form.is_valid() is False, "Should be invalid if no data given"


def test_article_form_with_missing_content():
    form = forms.ArticleForm(data={})
    assert form.is_valid() is False, "Should be invalid if missing data"
    assert "content" in form.errors, "Should have content field error"


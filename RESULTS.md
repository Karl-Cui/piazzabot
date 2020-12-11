# Results and Analysis

Below is documentation of several approaches we tried and their results. This is also justification for several design decisions.

## Data

Our corpus consisted of just the questions posted by students of the spring 2020 CSC148 Piazza. Since there are possibly several versions of a question in the raw CSV, we took the latest update of every question. We also have a method for generating a list of followups which were likely questions, however that was not used much. 

Please see `data_loader.py` for more details.

All of the below tests were conducted on the second assignment (ie. those under the assignment 2 folder). We found duplicates for all posts in the assignment 2 folder against all questions in the corpus. 

## Model Comparison and Number of Predictions

To start off, we want to find the best model to use and the optimal number `n` of predictions to give. Of course, giving more predictions would result in a higher accuracy (ie. the duplicate post being in one of the predicted posts), however we do not want to give students an excessive number of posts to read through, so we were experimenting with a range of 1 to 5 posts. The results are as follows:

```
n = 1
---------------------------------------
0.3621 for TFIDF
0.6092 for BERT
0.3276 for USE

n = 3
---------------------------------------
0.5575 for TFIDF
0.8161 for BERT
0.4943 for USE

n = 5
---------------------------------------
0.6264 for TFIDF
0.8735 for BERT
0.5402 for USE
```

__Clearly BERT performs the best out of the 3. Note that all 3 are methods of generating embeddings, and after that we use cosine similarity on all of them.__

There also seems to be an accuracy drop off--every subsequent prediction after the first one yields a smaller accuracy gain. This can be more clearly seen in this graph plotting the number of predictions and respective accuracies of BERT:

![](https://github.com/Karl-Cui/piazzabot/blob/master/imgs/num_predictions.png)

To this end we believe a reasonable number of possible duplicates to give to students may be 3 or 4. They have a decent accuracy and is not overwhelming for the student to look through.

Note: the numbers in the graph are different from the ones we just reported, because they take into account the time the questions were posted. See the next section.

## Use of Time Windows

The accuracies we previously generated are for when we considered the data as an entire dataset. However, __in a live scenario, new questions can only look at posts made so far for duplicates__. In addition to this, we want to determine whether there is a time window before the new question to filter by, since questions usually have a period of relevance.

We fixed the number of predictions to 3, and tried using several different time windows, ranging from 1 week to anytime before the current time.

```
TF-IDF
---------------------------------------
Timestamp-agnostic:     0.5575
Before current time:    0.4080
3 weeks before:         0.4080
2 weeks before:         0.3966
1 week before:          0.3563

BERT
---------------------------------------
Timestamp-agnostic:     0.8161
Before current time:    0.5690
2 weeks before:         0.5000
```

The accuracies are lower for both methods when we only consider question from earlier than the post rather than the entire corpus, but that is expected.

It seems that longer time windows correspond to higher accuracy. This suggests that the model is able to find most of the duplicate posts if they exist, and limiting the search for duplicates to an arbitrary time window before the question was posted actually __has nearly no effect or is detrimental__. With BERT, we attempted to plot different time windows ranging from 1 day to 3 weeks to illustrate this:

![](https://github.com/Karl-Cui/piazzabot/blob/master/imgs/time_windows.png)

There is a steep accuracy drop-off if we choose a time window of less than a week, and there does not seem to be too much of a difference if we chose windows of 2 or 3 weeks. Since the amount of extra computation from using a large window is marginal, __we decided to not set a time window and instead search for duplicates in all questions that are already posted.__

## Score / Confidence Thresholds

If most of the duplicates are above a certain score threshold (cosine similarity score) and most of the non-duplicates are below a threshold, then we can manually set a score threshold to automatically filter predictions. However, there does not seem to be a clear score to set a threshold at--the distribution of posts posts with duplicates is not easily separable from the distribution of posts with no duplicates:

![](https://github.com/Karl-Cui/piazzabot/blob/master/imgs/bert_sim_cutoff_n%3D3.png)

We also tried this for different numbers of predictions `n`, but found similar results in that the two distributions were hard to separate out with a simple threshold.

## Better than Piazza's Interal Recommendations?

Piazza has an internal question recommendation system, giving up to 10 posts the student may want to check before posting a question. Each of these recommendations is associated with a score, likely measuring confidence. We are not completely sure what Piazza's methods are, but from looking at the matches Piazza returns, __we hypothesize that Piazza's recommendation system is based on keyword detection and keyword matching__.

To compare Piazza's predictions and our predictions, we simulated posting the entire 2020 spring datasets' questions using [Piazza's unofficial API](https://github.com/hfaran/piazza-api/). For every question in the corpus, we first queried for Piazza's recommendations, and then actually post the question. This means that at every time step, we would be querying using only the questions that were posted thus far in the corpus. This effectively yielded a set of possible duplicates for every question, all of which were posted before the current question, effectively simulating the Piazza for that term.

We took a look at the distribution of Piazza's confidence scores, and the associated number of correct predictions at each score. The motivation was if there was a clear score cutoff, after which there are a large number of correct predictions, then we can directly use Piazza's recommendation system. However, there score distribution of correct predictions is also very spread out.

![](https://github.com/Karl-Cui/piazzabot/blob/master/imgs/piazza_pred_score_n%3D3.png)

To compare Piazza's predictions with ours, we took `n` questions with the highest scores from Piazza's predictions and checked whether there was a duplicate or not. The duplicate accuracies are as follows:

```
Piazza's recommendation accuracy
---------------------------------------
n = 1: 0.2244
n = 2: 0.3269
n = 3: 0.3910
n = 5: 0.4551
n = 10: 0.5064
```

For comparison, with `n = 3`, our model achieved `0.5690` accuracy, which is __significantly higher than Piazza's.__ Though we determined the the reasons behind why this is, we hypothesize this is due to __BERT being better at interpreting context than Piazza.__ Since BERT is bi-directional, at every point in a question it would have an understanding of the context before and after. Because of this context, through using BERT we may be able to better relate portions of questions, to find duplicates. This is based on our hypothesis that Piazza's recommendations are heavily keyword based and do not consider the context much.

## Future work

In many of these experiments, we did not go very in-depth. There are many avenues of investigation possible for future work:
- Weighted time windows: weigh the score for a possible duplicate by how long as it was posted. The function for weighting here may be linear to the time gap, but we suspect something like a [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function) may work better.
- Investigation into Piazza's recommendation algorithm, whether there are cases where Piazza's algorithm performs better or worse than BERT
- Using a score threshold that is a function of the scores. For example, filter by all questions that have a similarity score that is 1 standard deviation above the mean similarity score for a post, rather than setting a hard threshold.
- Fine tuning the model: all of our experiments were performed using a general, pretrained out-of-the-box BERT. We did not fine-tune it since we wanted to preserve the generality of the original BERT, however it would be a worthwhile experiment to try fine-tuning on Piazza posts, or a larger set of question data.

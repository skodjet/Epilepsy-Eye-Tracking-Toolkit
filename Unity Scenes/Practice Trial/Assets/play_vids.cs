using System.Collections;
using System.Collections.Generic;
// using System.IO.Ports;
using UnityEngine;
using UnityEngine.Video;
using UnityEngine.SceneManagement;

public class play_vids : MonoBehaviour
{
    public static int vids = 2; // Number of videos to play
    public VideoPlayer vp;
    public GameObject fixation;
    

    IEnumerator trial_coroutine(string[] video_paths)
    {

        for(int i = 0; i < vids; i++)
        {   
            // Prepare the video and show the fixation for 4 seconds.
            vp.url = video_paths[i];
            vp.Prepare();
            fixation.SetActive(true);
            yield return new WaitForSeconds(4f);

            // Play the video for 5 seconds.
            fixation.SetActive(false);
            vp.Play();
            yield return new WaitForSeconds(5f);
            Debug.Log("Finished playing video: " + i + "\n");

            vp.Pause();
        }

        Debug.Log("Trial finished\n");


    }


    // Start is called before the first frame update
    void Start()
    {

        string[] video_paths = 
        {
                                Application.dataPath + "\\Videos\\Theater.mp4", 
                                Application.dataPath + "\\Videos\\BasketballCourt.mp4"
                                
        };

        StartCoroutine(trial_coroutine(video_paths));
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}

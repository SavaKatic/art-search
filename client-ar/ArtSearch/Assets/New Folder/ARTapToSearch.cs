﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.Networking;

using UnityEngine.XR.ARSubsystems;
using System;

enum AppStage
{
    SEARCHING,
    RETRIEVING
}

public class ARTapToSearch : MonoBehaviour
{
    public GameObject PlacementIndicator;
    public GameObject SearchIndicator;
    public GameObject objectToPlace;

    private Pose PlacementPose;
    private ARRaycastManager RaycastManager;
    private ARPlaneManager PlaneManager;
    private bool PlacementPoseIsValid = false;
    private AppStage CurrentStage = AppStage.SEARCHING;

    private Texture2D m_Texture;


    void Start()
    {
        RaycastManager = FindObjectOfType<ARRaycastManager>();
        PlaneManager = FindObjectOfType<ARPlaneManager>();

        m_Texture = new Texture2D(Screen.width, Screen.height, TextureFormat.RGB24, true);
    }

    void Update()
    {
        UpdatePlacementPose();
        UpdateIndicator();

        if (PlacementPoseIsValid && Input.touchCount > 0 && Input.GetTouch(0).phase == TouchPhase.Began)
        {
            OnTouchAction();
        }
    }

    private void OnTouchAction()
    {
        if (CurrentStage == AppStage.SEARCHING) {
            FetchData();
        } else if(CurrentStage == AppStage.RETRIEVING) {
            PlaceInfo();
        }
    }

    private void PlaceInfo()
    {
        Instantiate(objectToPlace, PlacementPose.position, PlacementPose.rotation);
        CurrentStage = AppStage.SEARCHING;
    }

    private void FetchData()
    {
        // take screenshot
        // do the search
        // change stage

        m_Texture.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0, true);
        m_Texture.Apply();

        SearchForArt();

        CurrentStage = AppStage.RETRIEVING;
    }

    private void SearchForArt()
    {
        WWWForm form = new WWWForm();
        form.AddBinaryData("image[]", m_Texture.EncodeToPNG());

        UnityWebRequest request = UnityWebRequest.Post("http://localhost:8000/api/v1/search-artworks/", form);
        request.SetRequestHeader("Content-Type", "application/json");
        request.SendWebRequest();

    }

    private void UpdateIndicator()
    {
        var indicator = GetCurrentIndicator();
        var otherIndicator = GetInactiveIndicator();
        indicator.SetActive(PlacementPoseIsValid);
        otherIndicator.SetActive(false);
        if (PlacementPoseIsValid)
        {
            indicator.transform.SetPositionAndRotation(PlacementPose.position, PlacementPose.rotation);
        }
	}

    private GameObject GetCurrentIndicator()
    {
        if(CurrentStage == AppStage.SEARCHING) {
            return SearchIndicator;
        } else if(CurrentStage == AppStage.RETRIEVING) {
            return PlacementIndicator;
        } 
        return SearchIndicator;
    }

    private GameObject GetInactiveIndicator()
    {
        if(CurrentStage == AppStage.SEARCHING) {
            return PlacementIndicator;
        } else if(CurrentStage == AppStage.RETRIEVING) {
            return SearchIndicator;
        } 
        return PlacementIndicator;
    }

    private void UpdatePlacementPose()
	{
        // find where to cast indicator
        var screenCenter = Camera.current.ViewportToScreenPoint(new Vector3(0.5f, 0.5f));
        var hits = new List<ARRaycastHit>();
        RaycastManager.Raycast(screenCenter, hits, TrackableType.Planes);

        PlacementPoseIsValid = hits.Count > 0;
        if (PlacementPoseIsValid)
		{
            PlacementPose = hits[0].pose;

            ARPlane detectedPlane = PlaneManager.GetPlane(hits[0].trackableId);
            PlacementPose.rotation = Quaternion.FromToRotation(Vector3.up, detectedPlane.normal);
		}
	}
}
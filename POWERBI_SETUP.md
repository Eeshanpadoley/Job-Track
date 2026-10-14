# JobTrack 2.0 — Power BI Desktop setup

## Import data
1. Sign in to JobTrack locally.
2. Open **Power BI** in the sidebar and download `jobtrack_powerbi_data.csv`.
3. In Power BI Desktop choose **Home → Get data → Text/CSV**, select the CSV, then **Load**.
4. In the Fields/Data pane, rename the imported table to `JobTrack` if it has a different name.
5. Set `ApplicationDate` and `FollowUpDate` to Date data types. Set `DaysSinceApplied` to Whole number.
6. Save your report as `JobTrack_PowerBI.pbix` on your computer.

## DAX measures
```DAX
Total Applications = COUNTROWS(JobTrack)

Interviews =
CALCULATE(COUNTROWS(JobTrack), JobTrack[Status] = "Interview")

Offers =
CALCULATE(COUNTROWS(JobTrack), JobTrack[Status] = "Offer")

Rejections =
CALCULATE(COUNTROWS(JobTrack), JobTrack[Status] = "Rejected")

Pending Applications =
CALCULATE(
    COUNTROWS(JobTrack),
    JobTrack[Status] IN {"Applied", "Assessment", "On Hold", "Pending"}
)

Interview Rate = DIVIDE([Interviews], [Total Applications], 0)

Offer Rate = DIVIDE([Offers], [Total Applications], 0)

Rejection Rate = DIVIDE([Rejections], [Total Applications], 0)
```
Format the three rates as Percentage. `Pending Applications` counts only the status labels listed above; adjust the set if you use different labels.

## Suggested visuals
- KPI cards: Total Applications, Interviews, Offers, Rejections, Pending Applications, Interview Rate.
- Clustered bar chart: Company by Total Applications.
- Donut chart: Status by Total Applications.
- Bar chart: Source by Total Applications.
- Column chart: ApplicationMonth by Total Applications.
- Table: Company, JobTitle, Status, ApplicationDate, RequiredSkills.
- Slicers: Status, Source, Location, ApplicationMonth.

## Refresh workflow
This local version exports a snapshot CSV for the currently signed-in user. After adding or editing applications, download a fresh CSV and replace the old file at the same path before using **Refresh** in Power BI Desktop. For an always-live embedded report, a Power BI Service workspace, publishing/permissions and a secure embed configuration would need to be set up separately.

## Privacy
The Power BI export is scoped to the signed-in user and does not include interview notes, authentication data, or other users' applications. Do not commit exported personal application data or your `.pbix` with private information to a public GitHub repository.

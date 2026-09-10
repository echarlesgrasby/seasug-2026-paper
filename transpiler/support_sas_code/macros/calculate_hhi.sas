/* calculate_hhi.sas */

%MACRO CALCULATE_HHI__BASIC
/* This macro is still a work in progress... */
    (SOURCE=
    ,LIBRARY=WORK
    ,OUT_TBL_NAME=
    ,MKT_SHARE_COLUMN_NAME=
    ,GROUP_BY_COLUMN_NAME=);

    %PUT Calculating the Herfindahl-Hirschmann Index (HHI) off of base table &LIBRARY..&SOURCE. ;

    %LET BASE_HHI_QRY = "
                '0D0A'x
    ";
%MEND CALCULATE_HHI__BASIC;




/*

/* HHI with Utilities */
proc sql;
	select count(1) from work.hhi_util_base;	/* 387 base utilities */
quit;

proc sql;
	create table work.hhi_util_base as
	select gg.utility_name, sum(mw_cap) as mkt_share
	from
	(
		select p.utility_name, p.plant_name, p.plant_code, g.generator_id, g."NAMEPLATE_CAPACITY_(MW)"n as mw_cap
		from work.eia_source_plants p
		inner join work.eia_924_generators g
		on p.plant_code = g.plant_code
		where p.balancing_authority_code = 'SWPP'
	) gg
	group by gg.utility_name;
quit;

proc sql;
	select sum(g."NAMEPLATE_CAPACITY_(MW)"n) into :total_gen_capacity
	from work.eia_924_generators g
	inner join work.eia_source_plants p
	on p.plant_code = g.plant_code
	where balancing_authority_code = 'SWPP';
quit;

%PUT Total capacity in SPP according to EIA is: &total_gen_capacity. MW; /*100,008.6 MW */



proc sql;
	create table work.hhi_util_cplt as
	select utility_name, mkt_share, (mkt_share / &total_gen_capacity.) * 100 as mkt_share_pct
	from work.hhi_util_base
	order by utility_name asc;
quit;

proc sort data=work.hhi_util_cplt out=work.hhi_cplt_from_util; by DESCENDING mkt_share_pct ; run;

/* append a row_num on the sorted hhi_cplt dataset */
data work.hhi_util_with_num;
	row_num = _n_;
	set work.hhi_cplt_from_util;
run;

proc sql;
	select count(1) into :num_lower_firms from work.hhi_util_with_num where row_num > 20;
quit;

proc sql;
	create table work.hhi_utilities as
		select utility_name as firm_name, mkt_share_pct**2 as sqr_mkt_share_pct, hh.row_num as rn
		from work.hhi_util_with_num hh
		where row_num <= 20
	union
		select "Remaining Firms" as firm_name, (sum(mkt_share_pct**2) / &num_lower_firms.) as sqr_mkt_share_pct, 21 as rn
		from work.hhi_util_with_num
		where row_num > 20
		group by firm_name
	order by rn;
quit;

proc sql;
	select sum(sqr_mkt_share_pct) into :hhi_from_mw_capacity
	from work.hhi_utilities;
quit;


%PUT Herfindahl-Hirschmann Index as a function of nameplace capacity in SWPP: &hhi_from_mw_capacity.;


title 'HHI in SPP as a function of nameplace capacity';
footnote "Total Market HHI: %sysfunc(putn(&hhi_from_mw_capacity., 8.1))";
proc sgplot data=work.hhi_utilities;
	vbar firm_name / response=sqr_mkt_share_pct datalabel fillattrs=(color=steelblue);
	xaxis label="Resource Owner" discreteorder=data;
	yaxis label="HHI Contribution";
run;

*/
import React, { Component } from "react";
import { Button } from "react-bootstrap";
import "./NewAssetRequest.scss";
import { contains, getDateSS } from "../main.js";
import Request from "./components/Request";

// https://xd.adobe.com/view/2856aec3-f800-48bc-5922-bdfc629bf833-5e67/?fullscreen

class NewAssetRequest extends Component {
  state = {
    request_list: [
      {assetType:"Heavy Tanker",startDateTime:new Date("2020-04-28T17:50"),endDateTime:new Date("2020-05-01T14:50")}
    ],
  };

  processAssetRequest = () => {
    console.clear();
    /* This function needs to: 
            1. convert this.state.request_list into a list of the form [{assetId, startDateTime, endDateTime}]
            2. Pass that list to the assetRequestContainer via this.state.updateRequestList
            3. convert this.state.request_list into the list expected by the backend [{id/timeblock/timeblock}] 
            4. pass that list to the backend
            5. receive the recommendation list from the backend 
            6. Pass the recommendation list to the assetRequestContainer via onDisplayRequest(list)
            */
    // 1.
    const request_list = this.state.request_list;
    let idDateList = [];
    for (let i = 0; i < request_list.length; i++) {
      let temp = {};
      temp["assetId"] = i + 1;
      temp["startDateTime"] = request_list[i].startDateTime;
      temp["endDateTime"] = request_list[i].endDateTime;
      idDateList.push(temp);
    }
    // 2.
    this.props.updateRequestList(idDateList);
    // 3.
    let asset_list = [];
    for (let i = 0; i < request_list.length; i++) {
      let temp = {};
      temp["assetId"] = i + 1;
      temp["assetClass"] = request_list[i].assetType;
      temp["startTime"] = this.toTimeblock(request_list[i].startDateTime);
      temp["endTime"] = this.toTimeblock(request_list[i].endDateTime);
      asset_list.push(temp);
    }
    console.log(asset_list);
    // 4. TODO

    // 5. TODO
    let list = []; //should be the list returned by the backend

    // 6.
    // this.props.onDisplayRequest(list);
  };

  toTimeblock = (date) => {
    let day = date.getDay() * 48;
    let hours = date.getHours() * 2;
    let minutes = date.getMinutes() === 0 ? 0 : 1;
    return day + hours + minutes;
  };

  constructor(props) {
    super(props);
    this.insert_assetType = React.createRef();
    this.insert_startDateTime = React.createRef();
    this.insert_endDateTime = React.createRef();
    this.output = React.createRef();
  }

  Insert_Asset = () => {
    // Get Data
    console.clear();
    let a = {
      assetType: this.insert_assetType.current.value,
      startDateTime: new Date(this.insert_startDateTime.current.value),
      endDateTime: new Date(this.insert_endDateTime.current.value),
    };

    // Validate Data
    for (let x in a)
      if (!contains(a[x]) || a[x] == "Invalid Date") {
        alert(x + " not entered");
        return;
      }
    const o = this.state.request_list;
    for (let x of o)
      if (JSON.stringify(a) === JSON.stringify(x)) {
        alert("Same Record already exists");
        return;
      }

    // Validated Successfully
    o.push(a);
    this.setState({ request_list: o });
  };

  Remove_Asset = (e) => {
    console.clear();
    const o = this.state.request_list;

    // Find and Remove Element
    for (let x in o) {
      let s = JSON.stringify(o[x]);
      if (contains(s) && s === e) delete o[x];
    }

    // Update Data
    this.setState({ request_list: o });
  };

  submit_onClick = () => {
    // Get Data
    console.clear();
    const o = this.state.request_list;

    // Validate Data
    if (o.length === 0) {
      alert("At least one asset needs to be selected");
      return;
    }

    // Validated Successfully
    console.log(o);
  };

  ValidateDateTimeInput = (e) => {
    console.clear();
    e = e.target;

    // Get & Check Value
    let v = new Date(e.value);
    if (!contains(v) || (v == "Invalid Date")) return;

    // Check Start and End Input Range
    if (e.getAttribute("name") === "start") {
      let v2 = new Date(this.insert_endDateTime.current.value);
      if ((contains(v2) && (v2 != "Invalid Date")) && (v >= v2)) {
        v = new Date();
        v.setMinutes(v.getMinutes() - 30);
      }
    } else {
      let v2 = new Date(this.insert_startDateTime.current.value);
      if ((contains(v2) && (v2 != "Invalid Date")) && (v <= v2)) {
        v = new Date();
        v.setMinutes(v.getMinutes() + 30);
      }
    }
    console.log(v);

    // Modify Value
    v.setSeconds(0);
    v.setMinutes(v.getMinutes() >= 30 ? 30 : 0);
    v = getDateSS(v);
    
    // Set Value
    e.value = v;
  };

  componentDidMount = () => {
    // Assign Current Time
    let t = new Date();
    t.setSeconds(0);
    t.setMinutes(t.getMinutes() >= 30 ? 30 : 0);
    this.insert_startDateTime.current.value = getDateSS(t);
    t.setMinutes(t.getMinutes() + 30);
    this.insert_endDateTime.current.value = getDateSS(t);
  };

  render() {
    return (
      <main-body>
        <h1>New Asset Request</h1>
        <hr />
        <container>
          <entry>
            <div>
              <label>Asset Type</label>
              <select ref={this.insert_assetType}>
                <option value="" selected disabled hidden>
                  Select asset type
                </option>
                <option>Heavy Tanker</option>
                <option>Light Unit</option>
              </select>
            </div>
            <div>
              <label>Start Time Date</label>
              <input type="datetime-local" onChange={this.ValidateDateTimeInput} name="start" ref={this.insert_startDateTime} />
            </div>
            <div>
              <label>End Time Date</label>
              <input type="datetime-local" onChange={this.ValidateDateTimeInput} name="end" ref={this.insert_endDateTime} />
            </div>
            <insert onClick={this.Insert_Asset}></insert>
          </entry>
          <hr></hr>
          <output ref={this.output}>
            {this.state.request_list.map((t) => (
              <Request
                assetType={t.assetType}
                startDateTime={t.startDateTime}
                endDateTime={t.endDateTime}
                Remove_Asset={this.Remove_Asset}
              />
            ))}
          </output>
          <hr></hr>
          <button
            className="type-1"
            onClick={() => this.props.onDisplayRequest([])}
          >
            Submit Request
          </button>

          <Button className="btn-med" onClick={this.processAssetRequest}>
            Calls the WIP 'processAssetRequest' function
          </Button>
        </container>
      </main-body>
    );
  }
}
export default NewAssetRequest;
